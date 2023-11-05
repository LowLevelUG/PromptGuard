from enum import Enum


class Limits(Enum):
    NEGATIVE_SENTIMENT_LIMIT = 0.5
    DEFAULT_TOKEN_LIMIT = 2048
    MAX_BODY_LEN = 10 * 1024
    RATE_LIMIT = "1 per 1 second"


class Defaults(Enum):
    LLM_RES_PLACEHOLDER = "RESPONSE_HERE"
    LLM_REQ_PLACEHOLDER = "PROMPT_HERE"
    VALIDATE_OPERATION = "VALIDATE"
    LLM_POST_INSTRUCTIONS = ""
    ASK_OPERATION = "ASK"


class Errors(Enum):
    AUTH_HEADER_MISSING = (
        "Your authorization header is missing. Register to get an access token"
    )
    INVALID_RES_JSON = (
        f"llm_req_struct should contain the string {Defaults.LLM_RES_PLACEHOLDER.value}"
    )
    INVALID_REQ_JSON = (
        f"llm_req_struct should contain the string {Defaults.LLM_REQ_PLACEHOLDER.value}"
    )
    BAD_URL_AND_PROFANITY = "Your prompt contains a bad URL and profanity. Please try again with a clean prompt."
    ASK_VIOLATION = "Sorry, the response for the prompt you provided contains violations. Try again."
    SERVER_PROBLEM = "There was a problem with our servers reaching the LLM. Please try again."
    BAD_URL_DETECTED = "Your prompt contains a bad URL. Please try again with a clean prompt."
    PROMT_INJECTION_DETECTED = "The input your provided is flagged as a prompt injection"
    BAD_PROMPT = "Your prompt contains profanity. Please try again with a clean prompt."
    TYPE_ERROR = "You have specified an invalid type for the request/response body"
    REGISTERED_STRUCT_NOT_FOUND = "The registered JSON structure was not found"
    INVALID_AUTH_TOKEN = "You have specified an invalid authorization token"
    EMAIL_TOKEN_MISMATCH = "The email and access token do not match"
    INTERNAL_SERVER_ERROR = "An internal server error has occurred"
    LLM_DOWN = "Sorry, our default LLM servers are currently down"
    BAD_SENTIMENT = "The prompt response violates our guidelines"
    TOKEN_LIMIT_EXCEEDED = "You have exceeded your token limit"
    BODY_LEN_EXCEEDED = "Body length exceeds the maximum size"
    INVALID_JSON = "You have specified an invalid JSON"
    NO_RES_FROM_REQ = "No response from request"
    NO_RES_FROM_LLM = "No response from LLM"
    PROFANITY = "Profanity detected"
    ERROR = "Error"


class ResCodes(Enum):
    CONTENT_LENGTH_EXCEEDED = 413
    INTERNAL_SERVER_ERROR = 500
    MISSING_ARGUMENTS = 422
    UNAUTHORIZED = 403
    BAD_REQUEST = 401
    CREATED = 201
    OK = 200


class ReqBody(Enum):
    CLIENT_GUIDELINES = "client_guidelines"
    LLM_RESP_STRUCT = "llm_resp_struct"
    LLM_REQ_STRUCT = "llm_req_struct"
    CLIENT_RES = "client_response"
    LLM_ENDPOINT = "llm_endpoint"
    ACCESS_TOKEN = "access_token"
    TOKEN_LIMIT = "token_limit"
    HF_INPUTS = "inputs"
    EMAIL = "email"


class ResBody(Enum):
    CREATED = "Your account has been created successfully. Use this token as your authorization token"
    REVOKED = "Your account has been successfully revoked"
    NO_VIOLATIONS = "No violations detected"
    HF_TEXT_SUMMARY = "summary_text"
    ACCESS_TOKEN = "access_token"
    HF_NEGATIVE = "Negative"
    VIOLATION = "Violation"
    MESSAGE = "message"
    HF_LABEL = "label"
    HF_SCORE = "score"
    STATUS = "status"
    OK = "OK"


class SwaggerDocs(Enum):
    TITLE = "Prompt Validator API"
    OPENAPI_VERSION = "3.0.2"
    ROUTE = "/apidocs"
