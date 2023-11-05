## Introduction - Prompt Filtration System
+ As many companies move to LLMs to accomplish their text-generation needs, such as email generation and report generation, companies also put themselves in a position where their employees may get vulnerable/unacceptable responses from their LLMs. This is because of prompt injection vulnerabilities in LLMs.
+ What this software aims to do is to serve as a sanitation and verification framework/middle-ware which would perform sanitation on the entered prompt by the user, feed it to an LLM, and verify the received response to make sure it is a valid answer. This is done to prevent prompt injection attacks.

## API Endpoints
---
### POST /register
+ This endpoint is used to register a client with the prompt filtration system. The client should POST his email address to this endpoint. Our API will be using the HuggingFace LLM APIs by default, but the client can mention his own LLM API endpoint when registering so that his prompts will be processed by the LLM endpoint he specifies. He also needs to write a description about his company, so that the responses of prompts will be checked/validated again his company description.

#### Request Body
```json
{
	"email"			: "user@random.mail",
	"client_guidelines"	: "I am an employee of a company named ABC Ltd, which is an IT consulting company which works with some of the best companies. ABC Ltd is situated in Sri Lanka. I need to generate an email. I will provide you with a short description of the Email. The email should be easy to read and should not contain any negativity/profanity.",
	"llm_endpoint"	        : "http://api.abcltd.com/LLM_Endpoint",
	"llm_req_struct"	: { "promptMightGoHere" : {"prompt" : "PROMPT_HERE" }},
	"llm_resp_struct"       : { "responseOfLLM" : "RESPONSE_HERE" },
	"token_limit"	        :  1000
}
```

+ `email` : The email of the user.
+ `client_guidelines` : The rules/guidelines the response of an LLM's prompt should follow.
+ `llm_endpoint` : The API endpoint of the client's custom LLM.
+ `llm_req_struct` :The JSON structure we are expected to send to the LLM. The prompt will be replaced in place of "PROMPT_HERE".
+ `llm_resp_struct` : The JSON structure of the LLM API's expected response. The string "RESPONSE_HERE" is used to identify where in the JSON structure the prompt lies. This string will be replaced with the response of the LLM's server.
+ `token_limit` : The token limit of the LLM.

#### Response Body
```json
{
    "access_token": "01H6TNA716DY2SJ27MNY75N798",
    "message": "Your account has been created successfully"
}
```

+ `access_token` : The token the user should use as his bearer authentication token.
+ `message` : A short description describing if the user successfully created his account.

##### Register Process - Workflow
1) **Required parameters** - Checks for the availability of email and client guidelines in the request body.

2) **Custom LLM validation** - This is an optional feature that allows to register a client with a custom LLM. This phase validates the parameters in the request body that is required for LLM and checks for the strings "PROMPT_HERE" and "RESPONSE_HERE" in the relevant LLM Request and Response structures.

3) **Email validation** - Checks if the provided email is of a proper format.

4) **Client registration** - After all the validations have passed, a random access token is generated. The client details along with the token is inserted to the database.

---

### DELETE /revoke
+ The /revoke endpoint is used to delete a record. A DELETE request containing client's email should be sent along with the Authorization header. The endpoint will delete a record that matches the email and access token.

#### Request Headers

| Header        | Value               | Description                                                      |
| ------------- | ------------------- | ---------------------------------------------------------------- |
| Authorization | Bearer ACCESS_TOKEN | Required. The access token for authentication and authorization. |

#### Request Body
```json
{
	"email" : "user@random.mail"
}
```

+ `email` : The email of the user.

#### Response Body
```json
{
    "message": "Your account has been successfully revoked"
}
```

##### Revoke Process - Workflow
1) **Authorization token validation** - Verifying the authenticity of a provided token.

2) **Deleting a record** - This step deletes the record that matches the access token and the email from the database.
--- 

### POST /validate
+ The /validate endpoint validates a the output of an LLM and validates if it contains any unprofessional content such as profanity or bad sentiment.

#### Request Headers

| Header         | Value                     | Description                                                      |
| -------------- | ------------------------- | ---------------------------------------------------------------- |
| Authorization  | Bearer ACCESS_TOKEN_HERE  | Required. The access token for authentication and authorization. |

#### Request Body
```json
{
  "client_response": "The output of the LLM"
}
```

+ `client_response`: The response submitted by the client for the validation process.

#### Response Body
```json
{
    "message": "No violations detected"
}
```

+ `message`: A message that explains the result of the validation process.

##### Validation Process - Workflow
1) **Retrieve the client’s guidelines** - This step involves extracting relevant guideline information from the access token to determine specific guidelines that the response should adhere to. 

2) **Profanity check** - In this step involves analyzing the response using profanity detection techniques to determine if it contains any offensive or inappropriate language.

3) **Validation check using the guidelines** - This step utilized the HuggingFace APIs or similar tools to perform natural language processing analysis on response. This evaluates the response based on the specific guidelines provided by the client.

4) **Check if all validations passed** - This step verifies if all previous checks and validations are successful. If the response passes all validations, the API will return a JSON object with a message field containing what kind of output was provided by the LLM. If there was profanity, the server will respond with a profanity detected message, or a Bad sentiment detected message if there was bad sentiment in the LLM’s output.

---

### POST /ask
+ This API endpoint allows clients to submit a prompt as POST along with Authorization header and receive a generated response based on certain validations and guidelines. The endpoint supports both a custom large language model (LLM) and a default HuggingFace model for generating the response.

#### Request Headers

| Header         | Value                     | Description                                                      |
| -------------- | ------------------------- | ---------------------------------------------------------------- |
| Authorization  | Bearer ACCESS_TOKEN_HERE  | Required. The access token for authentication and authorization. |

#### Request Body
```json
{
  "prompt": "Client's prompt"
}
```

+ `prompt`: The user’s input or the query.

#### Response Body
```json
{
    "message": "The output of the LLM"
}
```

+ `message`: If the response is validated and appears legal, API will output the generated response to the prompt. If the response is invalid, response will be empty.
