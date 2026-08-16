import requests, os

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
