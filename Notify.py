import requests
from Config import GOTIFY_URL, GOTIFY_TOKEN


def send(title, message):
    json_data = {
        "message": message,
        "title": title,
        "priority": 5,
        "extras": {"client::display": {"contentType": "text/markdown"}},
    }
    headers = {"Content-type": "application/json"}
    try:
        requests.post(
            f"{GOTIFY_URL}/message",
            json=json_data,
            params={"token": GOTIFY_TOKEN},
            headers=headers,
            timeout=60,
        )
        return True
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return False
