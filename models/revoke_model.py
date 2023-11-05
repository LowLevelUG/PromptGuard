from pydantic.types import Json
from pydantic.main import BaseModel
from pydantic.networks import EmailStr

from utils.db import db
from utils.enums import Errors, ReqBody, ResBody, ResCodes


# Pydantic model for the register route
class Revoke(BaseModel):
    email: EmailStr
    access_token: str

    # Delete the user from the database
    def revoke_user(self) -> Json:
        """Deletes the user from the database"""

        # Prepare the required parameters
        user_data: Json = {
            ReqBody.EMAIL.value: self.email,
            ReqBody.ACCESS_TOKEN.value: self.access_token,
        }

        try:
            # Delete the user from the database if user's token matches the given email
            exists = db.delete_one_data(user_data)
            if exists:
                return {ResBody.MESSAGE.value: ResBody.REVOKED.value}, ResCodes.OK.value
            else:
                return {
                    ResBody.MESSAGE.value: Errors.EMAIL_TOKEN_MISMATCH.value
                }, ResCodes.UNAUTHORIZED.value

        # Raise an error if an internal server error occurs
        except Exception:
            return {
                ResBody.MESSAGE.value: Errors.INTERNAL_SERVER_ERROR.value
            }, ResCodes.INTERNAL_SERVER_ERROR.value
