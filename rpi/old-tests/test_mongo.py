from pymongo import MongoClient

client = MongoClient(
    "mongodb://pi_mongo:hepl@192.168.68.74:27017/",
    authSource="smartcheers"
)

db = client.smartcheers

# Test
print(db.list_collection_names())
