
from flask import Flask, jsonify
import json


app = Flask(__name__)


# Chargement identité du Raspberry
with open("device_config.json") as f:
    device = json.load(f)



@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "online",
        "deviceId": device["deviceId"]
    })



@app.route("/device", methods=["GET"])
def get_device():

    return jsonify(device)



@app.route("/camera/<visit_id>", methods=["GET"])
def camera_access(visit_id):

    # temporaire :
    # plus tard on remplacera par MongoDB

    allowed_visit = "d3775d49"


    if visit_id != allowed_visit:

        return jsonify({
            "error": "invalid visit id"
        }), 403


    return jsonify({
        "message": "camera access granted",
        "visitId": visit_id,
        "deviceId": device["deviceId"]
    })



if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )
