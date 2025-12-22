#!/usr/bin/env python3
import random
from gpiozero import OutputDevice
from time import sleep, time

# GPIO Pins für das 74HC595 Schieberegister
SDI = OutputDevice(17)  # Daten
RCLK = OutputDevice(18)  # Latch (Register Clock)
SRCLK = OutputDevice(27)  # Shift Clock

# Definition der Würfel-Muster (8x8 Matrix)
DICE_PATTERNS = {
    1: [(0x10, 0xef)],
    2: [(0x04, 0xdf), (0x40, 0xf7)],
    3: [(0x04, 0xdf), (0x10, 0xef), (0x40, 0xf7)],
    4: [(0x44, 0xd7), (0x11, 0xeb)],
    5: [(0x44, 0xd7), (0x10, 0xef), (0x11, 0xeb)],
    6: [(0x6c, 0xd7), (0x6c, 0xeb)]
}


def hc595_shift(dat):
    """ Schiebt 8 Bit in das Register. """
    for i in range(8):
        SDI.value = bool(0x80 & (dat << i))
        SRCLK.on()
        SRCLK.off()


def update_display(row_data, col_data):
    """ Sendet 16 Bit (8 für Spalten, 8 für Zeilen) und aktiviert sie. """
    hc595_shift(col_data)
    hc595_shift(row_data)
    RCLK.on()
    sleep(0.001)
    RCLK.off()


def show_number(number, duration):
    """ Zeigt eine Zahl für eine bestimmte Zeitdauer an (Multiplexing). """
    start_time = time()
    while time() - start_time < duration:
        for row, col in DICE_PATTERNS[number]:
            update_display(row, col)
            sleep(0.002)  # Zeit für Multiplexing beibehalten für Helligkeit


def roll_dice():
    """ Verlangsamte Animation für das Würfeln. """
    print("Würfel rollt langsam aus...")

    # Die Animation wird schrittweise langsamer
    durations = [0.2, 0.2, 0.3, 0.3, 0.4, 0.5]

    for d in durations:
        num = random.randint(1, 6)
        show_number(num, d)

    final_num = random.randint(1, 6)
    print(f"Ergebnis: {final_num}")
    # Zeige das Endergebnis deutlich länger an
    show_number(final_num, 5.0)


def main():
    print("Drücke Strg+C zum Beenden.")
    while True:
        roll_dice()
        print("Warte auf nächsten Wurf...")
        sleep(2.0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        update_display(0x00, 0xff)
        print("\nProgramm beendet.")