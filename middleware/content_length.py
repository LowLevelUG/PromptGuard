from functools import wraps

from flask.globals import request
from pydantic.types import Json

from utils.enums import Errors, Limits, ResCodes


# This is meant to be a middleware to validate the content length
def validate_content_length(f):
    """A wrapper to confirm if the content length exceeds the limit"""

    @wraps(f)
    def decorated(*args, **kwargs) -> Json:
        content_length: int = request.content_length or 0

        # Check if content limit exceeds the limit
        if (content_length) > Limits.MAX_BODY_LEN.value:
            return (
                {"Error": Errors.BODY_LEN_EXCEEDED.value},
                ResCodes.CONTENT_LENGTH_EXCEEDED.value,
            )

        return f(*args, **kwargs)

    return decorated
