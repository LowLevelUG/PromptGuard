import re
from json import loads

from pydantic.types import Json
from flask.globals import request
from flask.blueprints import Blueprint
from profanity_check import predict

from models.ask_model import Ask
from utils.enums import Errors, ResBody, ResCodes, Limits
from middleware.token_exists import validate_token
from middleware.content_length import validate_content_length
from utils.rate_limit import init_limiter

ask_bp: Blueprint = Blueprint("ask", __name__)
ask_limiter = init_limiter(ask_bp)

@ask_bp.post("/ask")
@ask_limiter.limit(Limits.RATE_LIMIT.value)
@validate_content_length
@validate_token
def ask() -> Json:
    """Asks the LLM a question
    User can specify a question and the LLM will respond with an answer
    ---
    tags:
      - Prompt Handling
    summary: Sends a prompt to an LLM and gets a safe response
    description: Takes in a prompt and replies with a professional response.
    operationId: askPrompt
    parameters:
      - in: query
        name: allowInsecure
        schema:
          type: boolean
        description: Whether to allow insecure prompts
    requestBody:
      description: Send in the prompt
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Ask'
      required: true
    responses:
      '200':
        description: Successful operation
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AskResponse'
    """

    # Prepare the input data
    request_body: Json = loads(request.data)
    query_params: dict = request.args.to_dict()
    allowInsecure: bool = query_params.get("allowInsecure") == "true"
    access_token: str = str(request.headers.get("Authorization")).split(" ")[1]
    request_body.update({"access_token": access_token})

    # Validate the request body and fetch the user's properties
    try:
        askInstance: Ask = Ask(**request_body)
        askInstance.get_properties()

    except Exception:
        return {
            ResBody.MESSAGE.value: Errors.INVALID_JSON.value
        }, ResCodes.BAD_REQUEST.value

    # Profanity check within the prompt
    if not allowInsecure:
        # First split the prompt to an array
        str_arr = re.split(r'[\n .,]', request_body['prompt'])
        str_arr = predict(str_arr)

        if 1 in str_arr:
            return {
                ResBody.MESSAGE.value: Errors.BAD_PROMPT.value
            }, ResCodes.BAD_REQUEST.value

    # If the user has specified a custom endpoint when registering
    match bool(askInstance.llm_endpoint):
        case True:
            # Send the prompt to the custom LLM endpoint
            res = askInstance.custom_send()
            if allowInsecure: return {ResBody.MESSAGE.value: res}, ResCodes.OK.value
            safe: Json | bool = askInstance.check_violations(res)
            if isinstance(safe, dict):
                return {
                    ResBody.MESSAGE.value: Errors.ASK_VIOLATION.value
                }, ResCodes.BAD_REQUEST.value
            else:
                return {ResBody.MESSAGE.value: res}, ResCodes.OK.value

        case False:
            # Send the prompt to the HuggingFace chatbot
            res = askInstance.hugchat_send()
            if allowInsecure: return {ResBody.MESSAGE.value: res}, ResCodes.OK.value
            safe: Json | bool = askInstance.check_violations(res)
            if isinstance(safe, dict):
                return {
                    ResBody.MESSAGE.value: Errors.ASK_VIOLATION.value
                }, ResCodes.BAD_REQUEST.value
            else:
                return {ResBody.MESSAGE.value: res}, ResCodes.OK.value
