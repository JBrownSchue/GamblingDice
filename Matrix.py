#!/usr/bin/env python3
import random
from gpiozero import OutputDevice
from time import sleep, time

# GPIO Pins für das 74HC595 Schieberegister
SDI = OutputDevice(17)  # Daten
RCLK = OutputDevice(18)  # Latch (Register Clock)
SRCLK = OutputDevice(27)  # Shift Clock

# Definition der Würfel-Muster (8x8 Matrix)
# Wir definieren für jede Zahl, welche Zeilen in welchen Spalten leuchten sollen.
DICE_PATTERNS = {
    1: [(0x10, 0xef)],  # Ein Punkt in der Mitte (Zeile 4, Spalte 5)
    2: [(0x04, 0xdf), (0x40, 0xf7)],  # Zwei Punkte diagonal
    3: [(0x04, 0xdf), (0x10, 0xef), (0x40, 0xf7)],  # Drei Punkte diagonal
    4: [(0x44, 0xd7), (0x11, 0xeb)],  # Vier Ecken (vereinfacht)
    5: [(0x44, 0xd7), (0x10, 0xef), (0x11, 0xeb)],  # Vier Ecken + Mitte
    6: [(0x6c, 0xd7), (0x6c, 0xeb)]  # Zwei Reihen à drei Punkte
}


def hc595_shift(dat):
    """ Schiebt 8 Bit in das Register. """
    for i in range(8):
        SDI.value = bool(0x80 & (dat << i))
        SRCLK.on()
        SRCLK.off()
    # Wir rufen RCLK hier NICHT auf, da wir immer 16 Bit (2 Byte) am Stück senden wollen


def update_display(row_data, col_data):
    """ Sendet 16 Bit (8 für Spalten, 8 für Zeilen) und aktiviert sie. """
    hc595_shift(col_data)  # Zweites Register (Spalten/Kathoden)
    hc595_shift(row_data)  # Erstes Register (Zeilen/Anoden)
    RCLK.on()
    sleep(0.001)
    RCLK.off()


def show_number(number, duration):
    """ Zeigt eine Zahl für eine bestimmte Zeitdauer an (Multiplexing). """
    start_time = time()
    while time() - start_time < duration:
        for row, col in DICE_PATTERNS[number]:
            update_display(row, col)
            sleep(0.002)  # Kurze Pause für Helligkeit und Stabilität


def roll_dice():
    """ Animation für das Würfeln. """
    print("Würfel rollt...")
    for _ in range(10):  # 10 zufällige Zahlen schnell hintereinander
        num = random.randint(1, 6)
        show_number(num, 0.1)

    final_num = random.randint(1, 6)
    print(f"Ergebnis: {final_num}")
    # Zeige das Endergebnis für 3 Sekunden an
    show_number(final_num, 3.0)


def main():
    print("Drücke Strg+C zum Beenden.")
    while True:
        roll_dice()
        sleep(0.5)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        # Alles ausschalten beim Beenden
        update_display(0x00, 0xff)
        print("\nProgramm beendet.")