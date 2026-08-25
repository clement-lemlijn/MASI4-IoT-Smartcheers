from flask import Flask, request, jsonify, abort
from flask_httpauth import HTTPBasicAuth
from pymongo import MongoClient
from datetime import datetime
from functools import wraps
import re

app = Flask(__name__)
auth = HTTPBasicAuth()

# Authentification
USERS = {
    "admin": "motdepassefort123",
    "client1": "clientpass"
}

@auth.verify_password
def verify_password(username, password):
    if username in USERS and USERS[username] == password:
        return username
    return None

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["smartpub_db"]
collection = db["sensors"]

# Helper OData
def apply_odata(query, args):
    # $filter (très simplifié : "champ eq 'valeur'" ou "champ gt 25")
    if "$filter" in args:
        filt = args["$filter"]
        # Exemples supportés :
        # temperature gt 25
        # device_id eq 'ESP32-01'
        # timestamp ge 2025-01-01T00:00:00
        match = re.match(r"(\w+)\s+(eq|ne|gt|ge|lt|le)\s+(.+)", filt)
        if match:
            field, op, value = match.groups()
            value = value.strip("'\"")
            # Conversion type simple
            if value.replace(".", "").isdigit():
                value = float(value) if "." in value else int(value)
            elif "T" in value:  # date ISO
                value = datetime.fromisoformat(value.replace("Z", ""))

            mongo_op = {
                "eq": field,
                "ne": {"$ne": value},
                "gt": {"$gt": value},
                "ge": {"$gte": value},
                "lt": {"$lt": value},
                "le": {"$lte": value}
            }
            if op == "eq":
                query[field] = value
            else:
                query[field] = mongo_op[op]

    # $top / $skip
    top = int(args.get("$top", 100))
    skip = int(args.get("$skip", 0))

    # $orderby
    sort = []
    if "$orderby" in args:
        for part in args["$orderby"].split(","):
            part = part.strip()
            if " desc" in part.lower():
                sort.append((part.replace(" desc", "").replace(" DESC", ""), -1))
            else:
                sort.append((part.replace(" asc", "").replace(" ASC", ""), 1))

    return query, top, skip, sort

@app.route("/odata/Mesures", methods=["GET"])
@auth.login_required
def get_mesures():
    args = request.args
    query = {}
    query, top, skip, sort = apply_odata(query, args)

    cursor = collection.find(query)
    if sort:
        cursor = cursor.sort(sort)
    cursor = cursor.skip(skip).limit(top)

    # $select
    select = args.get("$select")
    if select:
        fields = {f.strip(): 1 for f in select.split(",")}
        fields["_id"] = 0
        cursor = collection.find(query, fields).skip(skip).limit(top)
        if sort:
            cursor = cursor.sort(sort)

    results = list(cursor)
    # Convertir ObjectId et datetime
    for r in results:
        if "_id" in r:
            r["_id"] = str(r["_id"])
        for k, v in r.items():
            if isinstance(v, datetime):
                r[k] = v.isoformat()

    return jsonify({
        "@odata.context": "$metadata#Mesures",
        "value": results
    })

@app.route("/odata/$metadata")
def metadata():
    return '''<?xml version="1.0" encoding="utf-8"?>
    <edmx:Edmx Version="4.0" xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx">
      <edmx:DataServices>
        <Schema Namespace="IoT" xmlns="http://docs.oasis-open.org/odata/ns/edm">
          <EntityType Name="Mesure">
            <Key><PropertyRef Name="id"/></Key>
            <Property Name="id" Type="Edm.String"/>
            <Property Name="device_id" Type="Edm.String"/>
            <Property Name="temperature" Type="Edm.Double"/>
            <Property Name="timestamp" Type="Edm.DateTimeOffset"/>
          </EntityType>
          <EntityContainer Name="Container">
            <EntitySet Name="Mesures" EntityType="IoT.Mesure"/>
          </EntityContainer>
        </Schema>
      </edmx:DataServices>
    </edmx:Edmx>''', 200, {"Content-Type": "application/xml"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)