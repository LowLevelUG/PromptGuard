from typing import Optional
from nltk.tokenize import word_tokenize

from requests.api import post
from pydantic.types import Json
from pydantic.main import BaseModel
from pydantic.networks import HttpUrl
from requests.exceptions import RequestException

from utils.huggingface import HuggingFace
from utils.enums import Defaults, Errors, Limits, ResBody, ResCodes
from utils.llm import find_in_json_res, find_key, json_find_and_replace


# The Pydantic model for the ask route
class Ask(BaseModel):
    prompt: str
    access_token: str
    token_limit: int = Limits.DEFAULT_TOKEN_LIMIT.value
    llm_endpoint: Optional[HttpUrl | bool] = False
    full_prompt: Optional[str | bool] = False
    req_struct: Optional[dict | bool] = False
    res_struct: Optional[dict | bool] = False

    # Gets the registered properties of the user
    def get_properties(self):
        """Gets all the user-specified settings from the access token"""

        hf = HuggingFace(Defaults.ASK_OPERATION.value, self.prompt, self.access_token)
        self.token_limit = hf.token_limit
        self.llm_endpoint = hf.endpoint
        self.full_prompt = hf.input
        self.req_struct = hf.req_struct
        self.res_struct = hf.res_struct

    # Used to check if the user's prompt is larger than the token limit
    def validate_token_len(self) -> Json:
        """Validates the length of the user's prompt"""

        exceeds: bool = len(word_tokenize(self.full_prompt)) > self.token_limit

        if not exceeds:
            return True
        else:
            return {
                ResBody.STATUS.value: Errors.TOKEN_LIMIT_EXCEEDED.value,
                ResBody.MESSAGE.value: Errors.TOKEN_LIMIT_EXCEEDED.value,
            }, ResCodes.BAD_REQUEST.value

    # Send the prompt to the custom LLM endpoint if the use has specified one
    def custom_send(self) -> str:
        """Sends the prompt to the custom LLM endpoint"""

        request: Json = json_find_and_replace(
            self.req_struct, Defaults.LLM_REQ_PLACEHOLDER.value, str(self.full_prompt)
        )

        headers: Json = {
            "Content-Type": "application/json",
        }

        response: Json = self.custom_send_request(request, headers)

        if not response == None:
            llm_res_key = find_key(self.res_struct, Defaults.LLM_RES_PLACEHOLDER.value)

            try:
                return str(find_in_json_res(response, str(llm_res_key)))
            except:
                return Errors.NO_RES_FROM_LLM.value
        else:
            return Errors.NO_RES_FROM_REQ.value

    # A helper function for sending a request to a custom LLM endpoint
    def custom_send_request(self, request, headers=None):
        try:
            response = post(str(self.llm_endpoint), json=request, headers=headers)
            response.raise_for_status()
            return response.json()
        except RequestException:
            return None

    # Uses the hugchat library to generate a response for a prompt
    def hugchat_send(self) -> str:
        """Sends the prompt to the HuggingFace chatbot"""

        hf = HuggingFace(
            Defaults.ASK_OPERATION.value, str(self.full_prompt), self.access_token
        )
        response: str = hf.send_gpt() or Errors.SERVER_PROBLEM.value
        return response

    # Validate if there are violations in the generated prompt
    def check_violations(self, res: str) -> Json | bool:
        """Checks if the prompt has any violations"""
        hf = HuggingFace(Defaults.VALIDATE_OPERATION.value, res, self.access_token)
        safe: Json | bool = hf.is_safe()
        return safe
