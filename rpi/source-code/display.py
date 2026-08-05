"""Aide à l'affichage sur l'écran LCD Grove (RGB backlight + texte)."""
import time
from grove_rgb_lcd import setText, setRGB

from config import PRODUCTS


def safe_setRGB(r, g, b):
    try:
        setRGB(r, g, b)
    except OSError:
        pass


def init_lcd():
    for i in range(5):
        try:
            safe_setRGB(0, 128, 100)
            return
        except OSError:
            print(f"I2C failure, retrying... ({i+1}/5)")
            time.sleep(1)
    print("Could not initialize LCD, continuing anyway...")


def format_item(item, panier):
    # Menu principal (chaîne simple) ou produit (dict)
    if isinstance(item, str):
        return item
    product_id = item["id"]
    label = item["label"]
    qty = panier.get(product_id, 0)
    suffix = f"x{qty}" if qty > 0 else ""
    espace = 14 - len(label) - len(suffix)
    return f"{label}{' '*max(espace, 1)}{suffix}"


def display_menu(menu, idx, panier):
    """Affiche le menu avec quantité à droite."""
    item1 = format_item(menu[idx], panier)
    item2 = format_item(menu[(idx + 1) % len(menu)], panier)
    setText(f"> {item1}\n  {item2}")


def display_panier(panier):
    """Affiche le panier de façon compacte."""
    if not panier:
        setText("Panier vide")
        return
    lignes = []
    ligne = ""
    for produit_id, quantite in panier.items():
        produit = next(p for p in PRODUCTS if p["id"] == produit_id)
        abr = f"{produit['label'][0]}:{quantite}"

        if len(ligne) + len(abr) + 1 <= 16:
            ligne += " " + abr if ligne else abr
        else:
            lignes.append(ligne)
            ligne = abr
    lignes.append(ligne)
    setText("\n".join(lignes[:2]))