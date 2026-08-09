#!/usr/bin/env python3

import time
import smbus
import RPi.GPIO as GPIO


# ============================================================
# I2C
# ============================================================

I2C_BUS = 1

DISPLAY_RGB_ADDR = 0x30
DISPLAY_TEXT_ADDR = 0x3E

bus = smbus.SMBus(I2C_BUS)


# ============================================================
# RGB BACKLIGHT - SGM31323 V5.0
# ============================================================

def _rgb_reg(reg, value):
    """Écrit un registre du contrôleur RGB."""
    bus.write_byte_data(
        DISPLAY_RGB_ADDR,
        reg,
        value
    )


def _init_rgb():
    """
    Initialise le contrôleur RGB SGM31323
    du Grove LCD RGB Backlight V5.0.
    """

    # Reset du SGM31323
    _rgb_reg(0x00, 0x07)

    # Le reset nécessite environ 200 µs
    time.sleep(0.001)

    # Active les trois LED en permanence
    _rgb_reg(0x04, 0x15)


def setRGB(r, g, b):
    """
    Définit la couleur du rétroéclairage.

    r, g, b : valeurs de 0 à 255
    """

    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))

    # V5.0 :
    # 0x06 = rouge
    # 0x07 = vert
    # 0x08 = bleu

    _rgb_reg(0x06, r)
    _rgb_reg(0x07, g)
    _rgb_reg(0x08, b)


def blinkRGB():
    """
    Fait clignoter le rétroéclairage.
    """

    _rgb_reg(0x04, 0x2A)

    # environ 1 seconde
    _rgb_reg(0x01, 0x06)

    # 50% ON / 50% OFF
    _rgb_reg(0x02, 0x7F)


def noBlinkRGB():
    """Désactive le clignotement."""

    _rgb_reg(0x04, 0x15)


# ============================================================
# LCD
# ============================================================

def textCommand(cmd):
    """Envoie une commande au contrôleur LCD."""
    bus.write_byte_data(
        DISPLAY_TEXT_ADDR,
        0x80,
        cmd
    )


def setText(text):
    """Affiche du texte sur les deux lignes du LCD."""

    textCommand(0x01)
    time.sleep(0.002)

    textCommand(0x0C)
    textCommand(0x28)

    time.sleep(0.002)

    count = 0
    row = 0

    for c in text:

        if c == '\n' or count == 16:

            count = 0
            row += 1

            if row == 2:
                break

            textCommand(0xC0)

            if c == '\n':
                continue

        count += 1

        bus.write_byte_data(
            DISPLAY_TEXT_ADDR,
            0x40,
            ord(c)
        )


def setText_norefresh(text):
    """Met à jour le texte sans effacer complètement l'écran."""

    textCommand(0x02)
    time.sleep(0.002)

    textCommand(0x0C)
    textCommand(0x28)

    time.sleep(0.002)

    count = 0
    row = 0

    while len(text) < 32:
        text += ' '

    for c in text:

        if c == '\n' or count == 16:

            count = 0
            row += 1

            if row == 2:
                break

            textCommand(0xC0)

            if c == '\n':
                continue

        count += 1

        bus.write_byte_data(
            DISPLAY_TEXT_ADDR,
            0x40,
            ord(c)
        )


# ============================================================
# INITIALISATION
# ============================================================

_init_rgb()
