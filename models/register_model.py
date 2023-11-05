from typing import Optional, Literal

from pydantic.main import BaseModel
from pydantic.networks import EmailStr, HttpUrl
from pydantic.types import Json
from ulid import ULID

from utils.db import db
from utils.enums import Defaults, Errors, Limits, ReqBody, ResBody, ResCodes
from utils.llm import find_key


# Pydantic model for the register route
class Register(BaseModel):
    email: EmailStr
    client_guidelines: str
    token_limit: Optional[int | bool] = False
    llm_req_struct: Optional[dict | bool] = False
    llm_endpoint: Optional[HttpUrl | bool] = False
    llm_resp_struct: Optional[dict | bool] = False

    # Create a user and save it to the database
    def register_user(self) -> tuple[dict[str, str | Json], Literal[201] | Literal[500]]:
        """Adds the user to the database"""

        # Prepare the required parameters
        user_data: Json = {
            ReqBody.EMAIL.value: self.email,
            ReqBody.CLIENT_GUIDELINES.value: self.client_guidelines,
            ReqBody.ACCESS_TOKEN.value: str(ULID()),
            ReqBody.TOKEN_LIMIT.value: self.token_limit
            or Limits.DEFAULT_TOKEN_LIMIT.value,
        }

        # Append the optional parameters if LLM endpoint is given
        if self.llm_endpoint:
            user_data.update(
                {
                    ReqBody.LLM_ENDPOINT.value: str(self.llm_endpoint),
                    ReqBody.LLM_REQ_STRUCT.value: self.llm_req_struct,
                    ReqBody.LLM_RESP_STRUCT.value: self.llm_resp_struct,
                }
            )

        # Save to the database and return the access token
        try:
            db.insert_one_data(user_data)
            return (
                {
                    ResBody.MESSAGE.value: ResBody.CREATED.value,
                    ResBody.ACCESS_TOKEN.value: user_data[ReqBody.ACCESS_TOKEN.value]
                },
                ResCodes.CREATED.value
            )

        # Raise an error if an internal server error occurs
        except Exception:
            return (
                {
                    ResBody.MESSAGE.value: Errors.INTERNAL_SERVER_ERROR.value
                },
                ResCodes.INTERNAL_SERVER_ERROR.value
            )

    # Validates if the provided LLM's request/response JSON structures are valid
    def validate_struct(self) -> tuple[dict[str, str], Literal[401]] | bool | None:
        """Validates if the user provided valid request/response JSON structures"""

        # No need JSON structures if no LLM endpoint was specified
        if self.llm_endpoint is False:
            return True

        # Check if the request/response JSON structures are valid
        try:
            # Checks if there is a "PROMPT_HERE" string in the given JSON
            req_exists: bool = bool(
                find_key(self.llm_req_struct, Defaults.LLM_REQ_PLACEHOLDER.value)
            )

            # Checks if there is a "RESPONSE_HERE" string in the given JSON
            res_exists: bool = bool(
                find_key(self.llm_resp_struct, Defaults.LLM_RES_PLACEHOLDER.value)
            )

        # If the user has specified an invalid type for the request/response body
        except TypeError:
            return (
                {
                    ResBody.MESSAGE.value: Errors.TYPE_ERROR.value
                },
                ResCodes.BAD_REQUEST.value
            )

        # Checks if the request/response JSON structures are valid
        match (req_exists, res_exists):
            # If both request and response JSON structures are invalid
            case (False, False):
                return (
                    {
                        ResBody.MESSAGE.value:
                            f"{Errors.INVALID_REQ_JSON.value} and {Errors.INVALID_RES_JSON.value}"
                    },
                    ResCodes.BAD_REQUEST.value
                )

            # If only request JSON structure is invalid
            case (False, True):
                return (
                    {
                        ResBody.MESSAGE.value: Errors.INVALID_REQ_JSON.value
                    },
                    ResCodes.BAD_REQUEST.value
                )

            # If only response JSON structure is invalid
            case (True, False):
                return (
                    {
                        ResBody.MESSAGE.value: Errors.INVALID_RES_JSON.value
                    },
                    ResCodes.BAD_REQUEST.value
                )

            # If both request and response JSON structures are valid
            case (True, True):
                return True
