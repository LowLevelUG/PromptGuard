from os import fstat
from pathlib import Path
from stat import S_ISFIFO
from sys import argv, stdin
from typing import Optional

from orjson import JSONDecodeError, dumps, loads
from pydantic.main import BaseModel
from pydantic.networks import EmailStr, HttpUrl
from pydantic.types import Json
from requests.api import delete, post
from requests.models import Response

# Constants
HOST: str = "34.87.172.91"
VALIDATE_ENDPOINT: HttpUrl = HttpUrl(f"http://{HOST}/validate")
REGISTER_ENDPOINT: HttpUrl = HttpUrl(f"http://{HOST}/register")
REVOKE_ENDPOINT: HttpUrl = HttpUrl(f"http://{HOST}/revoke")
ASK_ENDPOINT: HttpUrl = HttpUrl(f"http://{HOST}/ask")
ENDPOINT_URL: HttpUrl = HttpUrl(f"http://{HOST}/")
RESPONSE_STRUCTURE_PATH: Path = Path("response.json")
REQUEST_STRUCTURE_PATH: Path = Path("request.json")
CONFIG_PATH: Path = Path("config.json")
DEF_TOKEN_LIMIT: int = 2048


# Pydantic model for the validator config
class ValidatorConfig(BaseModel):
    api_token: Optional[str] = None
    email: Optional[EmailStr] = None
    guidelines: Optional[str] = None
    has_custom_llm: Optional[bool] = None
    llm_endpoint_url: Optional[HttpUrl] = None
    llm_request_structure: Optional[Json] = None
    llm_response_structure: Optional[Json] = None
    token_limit: Optional[int] = 0

    # Function for saving the API token to file
    def save(self) -> None:
        """Save the API token to the specified file."""

        json_data: Json = {f"api_token": self.api_token}

        with open(CONFIG_PATH, "wb") as f:
            f.write(dumps(json_data))
        return

    # Function for loading the API token from file
    def load(self) -> None:
        """Load the API token from the specified file."""

        try:
            with open(CONFIG_PATH, "rb") as f:
                json_data: Json = loads(f.read())
                self.api_token = json_data.get("api_token")
        except FileNotFoundError:
            print("config.json was not found")

    # Function for registering the user to the endpoint
    def registerEndpoint(self) -> None:
        """Post data to the specified endpoint."""
        url: HttpUrl = REGISTER_ENDPOINT
        body: Json = {
            "email": self.email,
            "client_guidelines": self.guidelines,
            "token_limit": DEF_TOKEN_LIMIT,
        }

        # Append custom LLM data if user specified
        if self.has_custom_llm:
            body.update(
                {
                    "llm_endpoint": str(self.llm_endpoint_url),
                    "llm_req_struct": self.llm_request_structure,
                    "llm_resp_struct": self.llm_response_structure,
                    "token_limit": self.token_limit,
                }
            )

        response: Response = post(str(url), json=body)

        # Save access token to config file
        if response.status_code == 201:
            self.api_token = response.json()["access_token"]
            self.save()
            print("Registration successful")

    # Function for loading the LLM structure from file
    def loadStructure(self) -> None:
        """Load the LLM request and response structure from file."""

        try:
            with open(REQUEST_STRUCTURE_PATH, "rb") as f:
                self.llm_request_structure = loads(f.read())
            with open(RESPONSE_STRUCTURE_PATH, "rb") as f:
                self.llm_response_structure = loads(f.read())

        except FileNotFoundError:
            print("File was not found")

        except JSONDecodeError:
            print("Invalid JSON structure")

    # Utility for querying an LLM
    def queryLLM(self, prompt: str) -> str:
        """Query an LLM to generate a response for a given prompt."""
        url: HttpUrl = ASK_ENDPOINT
        headers: Json = {"Authorization": f"Bearer {self.api_token}"}
        body: Json = {
            "prompt": prompt,
        }

        response: Response = post(str(url), headers=headers, json=body)

        if response.status_code == 200 or 401 or 403:
            return response.json()["message"]

        else:
            return "Error querying LLM"

    # Utility for validating an LLM's response
    def validateRes(self, client_response: str) -> bool:
        """Check if an LLM's response is free of unprofessional language."""
        url: HttpUrl = VALIDATE_ENDPOINT
        headers: Json = {"Authorization": f"Bearer {self.api_token}"}
        body: Json = {
            "client_response": client_response,
        }

        response: Response = post(str(url), headers=headers, json=body)

        if response.status_code == 200:
            message: str = response.json()["message"]
            print(message)
            return True

        else:
            print("There was an error processing your request")
            return False

    # Utility for revoking and deleting the user's API token
    def revokeToken(self, userEmail: EmailStr) -> None:
        """Revoke the user's API token."""
        url: HttpUrl = REVOKE_ENDPOINT
        headers: Json = {"Authorization": f"Bearer {self.api_token}"}
        data: Json = {"email": userEmail}
        response: Response = delete(str(url), headers=headers, json=data)

        if response.status_code == 200:
            print("Token revoked")
            self.api_token = None
            self.save()
        else:
            print("Error revoking token")


# Starter code for the CLI
def init() -> None:
    print("Register using `python main.py register` for registration")
    api_token = input("Enter your API token: ")

    config: ValidatorConfig = ValidatorConfig(api_token=api_token)
    config.save()


def register() -> None:
    try:
        email: str = str(input("Enter your email (Required): "))
        guidelines: str = str(input("Enter your guidelines (Required): "))
        has_custom_llm: bool = bool(
            input("Do you have a custom LLM (y/N): ").lower() == "y"
        )

        # Default values for unbound variables
        llm_endpoint_url = llm_request_structure = llm_response_structure = None
        token_limit: int = 0

        # If user specified a custom LLM endpoint
        if has_custom_llm:
            llm_endpoint_url: HttpUrl | None = HttpUrl(
                input("Enter your LLM's HTTP endpoint URL: ")
            )
            token_limit: int = int(input("Enter your token limit (Required): "))

    except:
        print("Invalid input type")
        return

    # Save the inputs to an object
    config = ValidatorConfig(
        email=email,
        guidelines=guidelines,
        has_custom_llm=has_custom_llm,
        llm_endpoint_url=llm_endpoint_url,
        llm_request_structure=llm_request_structure,
        llm_response_structure=llm_response_structure,
        token_limit=token_limit,
    )

    # Load the LLM structure from file
    config.loadStructure()

    # Post the data to the endpoint
    config.registerEndpoint()


# Function for querying an LLM
def ask(cli_args: list[str]) -> None:
    """Query an LLM to generate a response for a given prompt"""

    config: ValidatorConfig = ValidatorConfig()
    config.load()

    # If CLI input is not given, prompt the user
    if cli_args:
        prompt: str = " ".join(cli_args)

    # If input is piped
    elif S_ISFIFO(fstat(0).st_mode):
        prompt: str = stdin.read()

    else:
        prompt: str = input("Enter your prompt: ")

    response: str = config.queryLLM(prompt)
    print(response)


# Function for validating an LLM's response
def validate(cli_args: list[str]) -> bool:
    """Check if an LLM's response is free of unprofessional language"""

    config: ValidatorConfig = ValidatorConfig()
    config.load()

    # If CLI input is not given, prompt the user
    if cli_args:
        response: str = " ".join(cli_args)

    # If input is piped
    elif S_ISFIFO(fstat(0).st_mode):
        response: str = stdin.read()

    else:
        response: str = input("Enter your prompt: ")

    return config.validateRes(response)


# Function for revoking and deleting the user's API token
def revoke() -> None:
    """Revoke an API token"""

    config: ValidatorConfig = ValidatorConfig()
    config.load()
    userEmail: EmailStr = input("Enter your email: ")
    config.revokeToken(userEmail)


if __name__ == "__main__":
    try:
        args = argv[1]

        if args == "init":
            init()
        elif args == "register":
            register()
        elif args == "ask":
            ask(argv[2:])
        elif args == "validate":
            validate(argv[2:])
        elif args == "revoke":
            revoke()

    except Exception as e:
        print(e, type(e))
        print("Usage: python main.py [init, register, ask, validate, revoke]")
