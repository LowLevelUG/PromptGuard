from functools import wraps

from flask.globals import request
from pydantic.types import Json

from utils.db import db
from utils.enums import Errors, ResCodes, ResBody


# Used to query the database to check if the token exists
def valid(access_token) -> bool:
    """A helper function to check if the token exists in the database"""

    exists: bool = bool(db.find_one_data({"access_token": access_token}))
    return exists


# This is a decorator function that will be used to validate the token
def validate_token(f):
    """A wrapper to confirm if the Authorization header is valid"""

    @wraps(f)
    def decorated(*args, **kwargs) -> Json:
        # Extract the token from the header or return False if it doesn't exist
        try:
            token: str | bool = str(request.headers.get("Authorization")).split(" ")[1]
        except:
            return (
                {ResBody.MESSAGE.value: Errors.AUTH_HEADER_MISSING.value},
                ResCodes.UNAUTHORIZED.value,
            )

        # Check if the token exist
        if not token:
            return (
                {ResBody.MESSAGE.value: Errors.AUTH_HEADER_MISSING.value},
                ResCodes.UNAUTHORIZED.value,
            )

        # Check if the token is valid
        elif not valid(token):
            return (
                {ResBody.MESSAGE.value: Errors.INVALID_AUTH_TOKEN.value},
                ResCodes.UNAUTHORIZED.value,
            )

        return f(*args, **kwargs)

    return decorated
