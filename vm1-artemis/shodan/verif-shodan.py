import requests
from datetime import datetime, timezone
from pymongo import MongoClient

def check_client_exposure(client_doc, db, webex_bot):
    ip = client_doc["ip_publique"]
    try:
        resp = requests.get(f"https://internetdb.shodan.io/{ip}", timeout=5)
    except requests.RequestException as e:
        # log l'échec de la requête elle-même
        return

    if resp.status_code == 404:
        # aucune info Shodan = rien d'exposé, tant mieux
        ports_detectes = []
    elif resp.status_code == 200:
        data = resp.json()
        ports_detectes = data.get("ports", [])
        cves = data.get("vulns", [])
    else:
        return

    ports_inattendus = [p for p in ports_detectes if p not in client_doc["ports_attendus"]]

    db.telemaintenance_events.insert_one({
        "client_id": client_doc["client_id"],
        "type": "audit_shodan",
        "timestamp": datetime.now(timezone.utc),
        "ports_detectes": ports_detectes,
        "ports_inattendus": ports_inattendus,
        "cves": cves if 'cves' in dir() else []
    })

    if ports_inattendus:
        webex_bot.send_alert(
            room_id=client_doc["webex_room_id"],
            message=f"⚠️ Port(s) inattendu(s) exposé(s) publiquement pour {client_doc['client_id']}: {ports_inattendus}"
        )
