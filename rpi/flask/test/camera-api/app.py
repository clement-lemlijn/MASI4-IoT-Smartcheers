from flask import Flask, jsonify
import json


app = Flask(__name__)


# Chargement config
with open("config.json") as f:
    config = json.load(f)


VISIT_ID = config["visitId"]



@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "online"
    })



@app.route("/camera/<visit_id>", methods=["GET"])
def camera(visit_id):

    if visit_id != VISIT_ID:
        return jsonify({
            "error": "invalid visit id"
        }), 403


    return jsonify({
        "message": "camera access granted",
        "visitId": visit_id
    })



if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )
