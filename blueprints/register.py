from json import dumps

from flask.blueprints import Blueprint
from flask.globals import request
from pydantic.types import Json

from middleware.content_length import validate_content_length
from models.register_model import Register
from utils.enums import Errors, ResBody, ResCodes, Limits
from utils.rate_limit import init_limiter

register_bp: Blueprint = Blueprint('register', __name__)

register_limiter = init_limiter(register_bp)

@register_bp.post('/register')
@register_limiter.limit(Limits.RATE_LIMIT.value)
@validate_content_length
def register() -> Json:
    '''Registers a new user
    User can register using this endpoint and get an access token
    ---
      tags:
        - Token Handling
      summary: Creates a new API token
      description: Takes in an email and returns an API token.
      operationId: registerUser
      requestBody:
        description: Create a new API token
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Register'
        required: true
      responses:
        '200':
          description: Successful operation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RegisterResponse'
    '''

    # Prepares the request data for Pydantic validation
    request_body: Json = dumps(request.json)

    # Validate the request body
    try:
        req_body: Register = Register.parse_raw(request_body)

    except Exception:
        return { ResBody.MESSAGE.value: Errors.INVALID_JSON.value }, ResCodes.BAD_REQUEST.value

    # Validate the request/response JSON structures

    struct_valid = req_body.validate_struct()

    # If response does not return a boolean, there was an error
    if not isinstance(struct_valid, bool):
        
        response, status = struct_valid or (None, ResCodes.BAD_REQUEST.value)
        return response, status

    # Register the user
    return req_body.register_user()
