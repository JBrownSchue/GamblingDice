#!/usr/bin/env python3
from gpiozero import OutputDevice
from time import sleep

# Definition der GPIO Pins für das 74HC595 Schieberegister
SDI = OutputDevice(17)  # Serial Data Input
RCLK = OutputDevice(18)  # Register Clock
SRCLK = OutputDevice(27)  # Shift Register Clock


def hc595_shift(dat):
    """ Schiebt 8 Bit Daten in das Register. """
    for i in range(8):
        # Wir prüfen das höchste Bit und wandeln es in True/False um
        SDI.value = bool(0x80 & (dat << i))
        SRCLK.on()
        SRCLK.off()
    # Übernimmt die Daten in den Ausgangsspeicher
    RCLK.on()
    sleep(0.001)
    RCLK.off()


def main():
    print("Schalte alle LEDs an... (Strg+C zum Beenden)")
    while True:
        # 1. Schiebe 0x00 für die Spalten (Kathoden an Masse/-)
        hc595_shift(0x00)
        # 2. Schiebe 0xFF für die Zeilen (Anoden an Plus/+)
        hc595_shift(0xff)

        sleep(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        # Beim Beenden alles ausschalten
        hc595_shift(0xff)  # Spalten aus
        hc595_shift(0x00)  # Zeilen aus
        print("\nTest beendet.")