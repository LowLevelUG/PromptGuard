## Installation

```
pip install -r requirements.txt
```

## Register
```
python main.py register
```

+ This should be the first command that you run to register yourself with the API. Your E-mail and client guidelines are required parameters. If you have a custom LLM, you will be prompted for extra details. On successful registration, you will get a unique access token, that will be saved in your `config.json` file.

+ The following is a registration without a custom LLM:

```
╰─ python main.py register

Enter your email (Required): user@random.mail

Enter your guidelines (Required): I am a cyber security analyst and I will be using you for asking questions about cyber security. Answer my questions in a professional language without any profanity.

Do you have a custom LLM (y/N): n

Registration successful
```

+ The following is a registration with a custom LLM:

```
╰─ python main.py register

Enter your email (Required): user@random.mail

Enter your guidelines (Required): I am a cyber security analyst and I need you to generate clean and professional answers to my questions

Do you have a custom LLM (y/N): y

Enter your LLM's HTTP endpoint URL: https://csinternship.pythonanywhere.com/

Enter your token limit (Required): 1024

Registration successful
```

+ The `request.json` and `response.json` file contents used when registering:

```
cat request.json

{
  "prompt": "PROMPT_HERE"
}


cat response.json

{
  "response": {
    "promptRes": {
      "res": "RESPONSE_HERE"
    },
    "status": "success"
  }
}
```

## Validate

```
python main.py validate <STRING TO VALIDATE>
```

+ This is the core validation function that will check a string for bad sentiment or profanity. Ideally, the output of an LLM has to be piped into this command. This has three outputs:
1. `"Response is free of unprofessional language"`
2. `"Response contains profanity"`
3. `"Response contains negative sentiment"`
4. `"Response contains both profanity and negative sentiment"`

+ The following is an example of as using piping the output of the `ask` endpoint's output into validate:
```
╰─ python main.py ask Hi how are you | python main.py validate

Response is free of unprofessional language
```

+ You can pipe the output of any command to `python main.py validate` and it will validate the given string. This functionality was intended for users who were not comfortable registering with our service with their custom LLM. These kinds of users can locally run LLM and pipe its outputs into our Python frontend validator.


## Ask

```
╰─ python main.py ask Generate me an email on asking a raise 

Hi there! I see you need help writing an email requesting a pay raise. Here's an example message that addresses all your points:

Subject: Request for Pay Raise Consideration at Next Performance Review

Dear [Manager],

I hope this email finds you well. Firstly, thank you again for your leadership and guidance over the past year; it has been greatly appreciated by everyone here at the company. Secondly, I am excited about the opportunity to continue growing my career within our team beyond my current role and responsibilities. And thirdly, I would like to formally ask if we can discuss my compensation during our next performance review later this month/year (please insert appropriate date). This is not only because of market conditions driving up salaries but also because my contributions deserve recognition as part of any merit increase process. I look forward to sharing more details on my achievements to support these comments when we meet in person to finalize. Thank you for considering and confirming back with me once possible.

Best regards,
[Your Name]
```

+ This is the endpoint that will take in a user-provided prompt and give out a response from an LLM:
    1. If the user provided a custom LLM on registration, that LLM will be used by the `\ask` endpoint.
    2. If the user does not provide a custom LLM on registration, one of our default LLM endpoints (HuggingFace) will be used.

+ The `\ask` functionality is guaranteed to generate only professional and safe prompts as all prompt responses will be validated before being sent out to the user.

## Revoke

```
╰─ python main.py revoke  

Enter your email: user@random.mail
Token revoked
```

+ This command will revoke your access token and delete it from your `config.json` file. You will have to register again to get a new access token.

+ The revoke will happen only if the user enters the same email that he used to register.
