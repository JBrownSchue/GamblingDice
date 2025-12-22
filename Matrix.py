#!/usr/bin/env python3
import random
from gpiozero import OutputDevice
from time import sleep, time

# GPIO Pins für das 74HC595 Schieberegister
SDI = OutputDevice(17)  # Serial Data Input
RCLK = OutputDevice(18)  # Register Clock
SRCLK = OutputDevice(27)  # Shift Register Clock

# Definition der sauberen Würfel-Punkte
# Zeilen (Anoden): 0x04 (Reihe 3), 0x10 (Reihe 5), 0x40 (Reihe 7)
# Spalten (Kathoden): 0xfb (Spalte 3), 0xef (Spalte 5), 0xbf (Spalte 7)
P = {
    'TL': (0x04, 0xfb), 'TR': (0x04, 0xbf),  # Top Left, Top Right
    'ML': (0x10, 0xfb), 'MC': (0x10, 0xef), 'MR': (0x10, 0xbf),  # Mid Left, Center, Mid Right
    'BL': (0x40, 0xfb), 'BR': (0x40, 0xbf)  # Bottom Left, Bottom Right
}

DICE_PATTERNS = {
    1: [P['MC']],
    2: [P['TL'], P['BR']],
    3: [P['TL'], P['MC'], P['BR']],
    4: [P['TL'], P['TR'], P['BL'], P['BR']],
    5: [P['TL'], P['TR'], P['BL'], P['BR'], P['MC']],
    6: [P['TL'], P['ML'], P['BL'], P['TR'], P['MR'], P['BR']]
}


def hc595_shift(dat):
    """ Schiebt 8 Bit in das Register. """
    for i in range(8):
        SDI.value = bool(0x80 & (dat << i))
        SRCLK.on()
        SRCLK.off()


def update_display(row_data, col_data):
    """ Sendet 16 Bit (Spalten dann Zeilen) und aktiviert sie. """
    hc595_shift(col_data)
    hc595_shift(row_data)
    RCLK.on()
    sleep(0.0005)  # Sehr kurze Zeit für die LED
    RCLK.off()


def show_number(number, duration):
    """ Multiplexing: Zeigt die Punkte einer Zahl sehr schnell nacheinander. """
    start_time = time()
    while time() - start_time < duration:
        for row, col in DICE_PATTERNS[number]:
            update_display(row, col)
            # Wichtig: Alles kurz ausschalten zwischen den Punkten gegen Geisterbilder
            update_display(0x00, 0xff)


def roll_dice():
    """ Verlangsamte Animation für das Ausrollen des Würfels. """
    print("Würfel rollt...")

    # Die Schritte werden immer langsamer (0.1s bis 0.6s)
    for speed in [0.1, 0.1, 0.2, 0.2, 0.3, 0.4, 0.6]:
        num = random.randint(1, 6)
        show_number(num, speed)

    final_num = random.randint(1, 6)
    print(f"Ergebnis: {final_num}")
    show_number(final_num, 5.0)  # Ergebnis für 5 Sekunden zeigen


def main():
    print("Drücke Strg+C zum Beenden.")
    while True:
        roll_dice()
        # Kurze Pause bevor der nächste automatische Wurf startet
        update_display(0x00, 0xff)
        sleep(1.0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        update_display(0x00, 0xff)
        print("\nProgramm beendet.")