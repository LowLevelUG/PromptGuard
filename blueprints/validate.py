from json import loads

from pydantic.types import Json
from flask.globals import request
from flask.blueprints import Blueprint

from models.validate_model import Validate
from utils.enums import Errors, ResBody, ResCodes, Limits
from middleware.token_exists import validate_token
from middleware.content_length import validate_content_length
from utils.rate_limit import init_limiter

validate_bp: Blueprint = Blueprint("validate", __name__)
validate_limiter = init_limiter(validate_bp)

@validate_bp.post("/validate")
@validate_limiter.limit(Limits.RATE_LIMIT.value)
@validate_content_length
@validate_token
def validate() -> Json:
    """Validates the client response
    User can pass in a response from an LLM and check if it violates professionalism
    ---
      tags:
        - Prompt Handling
      summary: Validates an LLM's prompt response
      description: Checks an LLM's prompt response for profanity or unprofessional tone.
      operationId: validatePrompt
      requestBody:
        description: Update an existent pet in the store
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ValidatePrompt'
        required: true
      responses:
        '200':
          description: Successful operation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ValidateResponse'
    """

    # Prepares the request data for Pydantic validation
    request_body: Json = loads(request.data)
    access_token: str = str(request.headers.get("Authorization")).split(" ")[1]
    request_body.update({"access_token": access_token})

    # Validate the request body
    try:
        req_body: Validate = Validate(**request_body)

    except Exception:
        return {ResBody.MESSAGE.value: Errors.INVALID_JSON.value}, ResCodes.BAD_REQUEST.value

    # Validate the client response
    return req_body.validate_res()
