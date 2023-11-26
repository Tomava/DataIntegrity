import requests
from Config import PUSHOVER_USER_KEY, PUSHOVER_API_KEY

URL = "https://api.pushover.net/1/messages.json"

def send(title, message):
    json_data = {"token": PUSHOVER_API_KEY, "user": PUSHOVER_USER_KEY, "message": message, "title": title, "html": 1}
    try:
        request = requests.post(URL, json=json_data)
        return True
    except:
        return False
