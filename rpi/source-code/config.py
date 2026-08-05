"""Chargement de la configuration MQTT et du catalogue produits pour SmartCheers."""
import json

with open("config.json", "r") as f:
    CONFIG = json.load(f)

RPI_ID = CONFIG["rpiId"]
BROKER_IP = CONFIG["mqtt"]["broker"]
BROKER_PORT = CONFIG["mqtt"]["port"]
MQTT_USERNAME = CONFIG["mqtt"]["username"]
MQTT_PASSWORD = CONFIG["mqtt"]["password"]

with open("products.json", "r") as f:
    PRODUCTS = json.load(f)


def get_products_by_category(category):
    return [p for p in PRODUCTS if p["categorie"] == category]


DRINKS = get_products_by_category("Boissons")
SNACKS = get_products_by_category("Snacks")