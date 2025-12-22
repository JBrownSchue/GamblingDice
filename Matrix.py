#!/usr/bin/env python3
import random
from gpiozero import OutputDevice
from time import sleep, time
from RPLCD.i2c import CharLCD  #

# --- Konfiguration LCD ---
I2C_ADDRESS = 0x27
I2C_PORT = 1

# --- LCD Initialisierung ---
try:
    lcd = CharLCD(i2c_expander='PCF8574', address=I2C_ADDRESS, port=I2C_PORT,
                  cols=16, rows=2, dotsize=8)
    lcd.backlight_enabled = True
except Exception as e:
    print(f"LCD Fehler: {e}")
    exit()

# --- Konfiguration Matrix ---
SDI = OutputDevice(17)
RCLK = OutputDevice(18)
SRCLK = OutputDevice(27)

# Punkt-Definitionen für die Matrix
P = {
    'TL': (0x04, 0xfb), 'TR': (0x04, 0xbf),
    'ML': (0x10, 0xfb), 'MC': (0x10, 0xef), 'MR': (0x10, 0xbf),
    'BL': (0x40, 0xfb), 'BR': (0x40, 0xbf)
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
    for i in range(8):
        SDI.value = bool(0x80 & (dat << i))
        SRCLK.on()
        SRCLK.off()


def update_display(row_data, col_data):
    hc595_shift(col_data)
    hc595_shift(row_data)
    RCLK.on()
    sleep(0.0005)
    RCLK.off()


def show_number(number, duration):
    start_time = time()
    while time() - start_time < duration:
        for row, col in DICE_PATTERNS[number]:
            update_display(row, col)
            update_display(0x00, 0xff)


def lcd_print(line1, line2=""):
    """ Hilfsfunktion um Text auf Terminal und LCD zu spiegeln. """
    print(f"{line1} {line2}")
    lcd.clear()  #
    lcd.cursor_pos = (0, 0)  #
    lcd.write_string(line1)  #
    if line2:
        lcd.cursor_pos = (1, 0)  #
        lcd.write_string(line2)  #


def roll_dice():
    lcd_print("Wuerfel rollt...")

    # Animation verlangsamen
    for speed in [0.1, 0.1, 0.2, 0.2, 0.3, 0.4, 0.6]:
        num = random.randint(1, 6)
        show_number(num, speed)

    final_num = random.randint(1, 6)
    lcd_print("Ergebnis:", f"Zahl {final_num}")
    show_number(final_num, 5.0)


def main():
    lcd_print("GamblingDice", "Ready to roll!")
    sleep(2)
    while True:
        roll_dice()
        lcd_print("Naechster Wurf", "in 2 Sek...")
        update_display(0x00, 0xff)
        sleep(2.0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        update_display(0x00, 0xff)
        lcd.clear()  #
        lcd.backlight_enabled = False  #
        print("\nProgramm beendet.")