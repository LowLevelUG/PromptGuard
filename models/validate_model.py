from pydantic.types import Json
from pydantic.main import BaseModel

from utils.huggingface import HuggingFace
from utils.enums import Defaults, ResBody, ResCodes


# Pydantic model for the validate route
class Validate(BaseModel):
    access_token: str
    client_response: str

    # Used to validate if a client response is professional & safe
    def validate_res(self) -> Json:
        """Validates the client response"""

        # Create HuggingFace class instance
        hf = HuggingFace(
            Defaults.VALIDATE_OPERATION.value, self.client_response, self.access_token
        )

        # Check for bad sentiment & profanity
        safe = hf.is_safe()

        # If these was an error, a JSON will return
        if type(safe) == dict:
            return safe, ResCodes.OK.value
        else:
            return {ResBody.MESSAGE.value: ResBody.NO_VIOLATIONS.value}, ResCodes.OK.value
