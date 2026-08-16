import requests

WEBEX_TOKEN = ""
HEADERS = {"Authorization": f"Bearer {WEBEX_TOKEN}", "Content-Type": "application/json"}

def create_bar_room(bar_name, support_emails):
    # 1. Créer la room
    r = requests.post("https://webexapis.com/v1/rooms",
                      headers=HEADERS,
                      json={"title": f"Smartcheers - Télémaintenance {bar_name}"})
    r.raise_for_status()
    room_id = r.json()["id"]

    # 2. Ajouter les membres de ton équipe support
    for email in support_emails:
        requests.post("https://webexapis.com/v1/memberships",
                      headers=HEADERS,
                      json={"roomId": room_id, "personEmail": email})

    return room_id

room_id = create_bar_room("Le Zinc", ["toi@smartcheers.be", "collegue@smartcheers.be"])
print(room_id)  # à stocker dans MongoDB