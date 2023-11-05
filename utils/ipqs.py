import re
import requests
import urllib.parse
from os import getenv
import json

def urlcheck(input_string: str) -> bool:
    apikey = str(getenv("IPQS_APIKEY"))
    ipqurl = "https://www.ipqualityscore.com/api/json/url/"+apikey+"/"

    def find(string):
        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        url = re.findall(regex, string)
        return [x[0] for x in url]

    urls = find(input_string)

    keys_to_check = {
        "unsafe": "unsafe",
        "phishing": "phishing",
        "suspicious": "suspicious",
        "adult": "adult"
    }

    unsafe = False  # flag to track unsafe urls

    try:
        for target in urls:
            response = requests.get(ipqurl + urllib.parse.quote_plus(target))
            response.raise_for_status()  # if request failed
            response_json = response.json()
            error_messages = [error_key for error_key in keys_to_check if response_json.get(keys_to_check[error_key])]

            if error_messages:
                print({"error": f"error! The prompt contains {'/'.join(error_messages)} URLs"})
                unsafe = True 

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")

    return unsafe

