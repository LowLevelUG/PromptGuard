import requests
from os import getenv

LAKERA_API = str(getenv("LAKERA_API"))

def is_flagged(prompt):
    print(prompt)
    response = requests.post(
        "https://api.lakera.ai/v1/prompt_injection",
        json={"input": prompt},
        headers={"Authorization": f"Bearer {LAKERA_API}"},
    )
    response = response.json()
    print(response)
    flagged = response['results'][0]['flagged']
    print(flagged)
    return flagged
