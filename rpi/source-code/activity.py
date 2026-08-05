"""Suivi d'inactivité utilisateur pour l'auto-annulation de session (timeout 5 min)."""
import time

INACTIVITY_TIMEOUT = 300  # secondes

_last_activity = time.time()


def touch_activity():
    """A appeler à chaque action utilisateur (joystick, bouton) pour reset le timer."""
    global _last_activity
    _last_activity = time.time()


def is_timed_out():
    return (time.time() - _last_activity) > INACTIVITY_TIMEOUT