import requests
import os

with open(".env") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ[key] = value

TOKEN = os.environ["WEBEX_BOT_TOKEN"]
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
def create_room_for_bar(nom_bar, support_emails):
    r = requests.post("https://webexapis.com/v1/rooms",
        headers=HEADERS, json={"title": f"Smartcheers - {nom_bar}"})
    r.raise_for_status()
    room_id = r.json()["id"]
    for email in support_emails:
        requests.post("https://webexapis.com/v1/memberships",
            headers=HEADERS, json={"roomId": room_id, "personEmail": email})
    return room_id
