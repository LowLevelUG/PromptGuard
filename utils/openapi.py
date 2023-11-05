config = {
    "openapi": "3.0.3",
    "info": {
        "title": "Prompt Validator - OpenAPI 3.0",
        "description": "This is the Swagger API documentation for the prompt validation/filtration framework. The API consists of four main endpoints:\n  1. `/register`: This is used to register a user to the system. He has to provide his email and a short description of the nature of his business (cient guidelines) after which he will get an API token that can be used throughout the API. User can specify a custom LLM endpoint's URL if he wants (optional) to base it for /ask and /validate operations.\n  \n  2. `/revoke`: This deletes a registered API token. It takes in the API token and its registered email, and deletes the API token.\n  \n  3. `/validate`: This is used to take in a prompt response (output of an LLM) and check if it contains profanity, bad tone, or anything that might be unprofessional in a business setting (if used for cooperate purposes like generating emails).\n  \n  4. `/ask`: This is used to take in a prompt, pass it to an LLM, and get a safe prompt response. If the user has registered with a custom LLM endpoint, it will be used for prompt response generation. The prompt-response that comes out of this endpoint is guaranteed to be safe and free from prompt-injection.",
        "version": "1.0.11",
    },
    "servers": [
        {"url": "/"},
        {"url": "http://34.87.172.91"},
    ],
    "tags": [
        {
            "name": "Token Handling",
            "description": "Relates to creation/deletion of API tokens.",
        },
        {
            "name": "Prompt Handling",
            "description": "Relates to validating and generating safe prompts/responses.",
        },
    ],
    "components": {
        "securitySchemes": {
            "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
        },
        "schemas": {
            "Register": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "format": "email",
                        "example": "user@random.mail",
                    },
                    "client_guidelines": {
                        "type": "string",
                        "example": "Generate me a response that is professional for the questions I ask. ",
                    },
                },
            },
            "RevokeToken": {
                "type": "object",
                "required": ["email"],
                "properties": {
                    "email": {
                        "type": "string",
                        "format": "email",
                        "example": "user@random.mail",
                    },
                },
            },
            "RevokeTokenResponse": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Client successfully deleted.",
                    }
                },
            },
            "RegisterResponse": {
                "type": "object",
                "properties": {
                    "access_token": {
                        "type": "string",
                        "example": "01H65K6ZN28HJ5R5HEB4HTK2G6",
                    },
                    "message": {
                        "type": "string",
                        "example": "Client successfully registered.",
                    },
                },
            },
            "ValidatePrompt": {
                "type": "object",
                "required": ["client_response"],
                "properties": {
                    "client_response": {
                        "type": "string",
                        "example": "I kindly hope you go and die in hell",
                    },
                },
            },
            "ValidateResponse": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Negative sentiment detected",
                    },
                },
            },
            "Ask": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "example": "How do lifetimes work in Rust?",
                    }
                },
            },
            "AskResponse": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "In Rust, lifetimes represent the maximum scope or lifetime of any references generated from those variables or expressions, ensuring their type safety and preventing memory unsafety issues such as null or dangling pointer references. Lifetime values indicate the largest enclosing scope where the reference will remain valid and guaranteed not to drop to zero. If you have any specific questions about using lifetimes in your own code or library development, feel free to ask me!",
                    }
                },
            },
        },
    },
    "security": [{"bearerAuth": []}],
}
