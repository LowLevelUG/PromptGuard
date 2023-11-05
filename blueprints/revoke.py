from json import dumps, loads

from pydantic.types import Json
from flask.globals import request
from flask.blueprints import Blueprint

from models.revoke_model import Revoke
from utils.enums import Errors, ResBody, ResCodes
from middleware.token_exists import validate_token
from middleware.content_length import validate_content_length

revoke_bp: Blueprint = Blueprint("revoke", __name__)


@revoke_bp.delete("/revoke")
@validate_content_length
@validate_token
def revoke() -> Json:
    """Revokes a user
    User can register using this endpoint and get an access token
    ---
      tags:
        - Token Handling
      summary: Delete an API token
      description: Takes in an API token and its email and deletes the API token if email is validated.
      operationId: revokeUser
      requestBody:
        description: Created user object
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/RevokeToken"

      responses:
        default:
          description: successful operation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RevokeTokenResponse'
    """

    # Prepares the request data for Pydantic validation
    request_body: Json = loads(request.data)
    access_token: str = str(request.headers.get("Authorization")).split(" ")[1]
    request_body.update({"access_token": access_token})
    request_body = dumps(request_body)

    # Validate the request body
    try:
        req_body = Revoke.parse_raw(request_body)

    except Exception:
        return {ResBody.MESSAGE.value: Errors.INVALID_JSON.value}, ResCodes.BAD_REQUEST.value

    # Revoke the user
    return req_body.revoke_user()
