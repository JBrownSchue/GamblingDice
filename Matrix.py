#!/usr/bin/env python3
import random
from gpiozero import OutputDevice, Button
from time import sleep, time
from RPLCD.i2c import CharLCD  #

# --- Hardware Setup ---
I2C_ADDRESS = 0x27  #
I2C_PORT = 1

SDI = OutputDevice(17)  #
RCLK = OutputDevice(18)  #
SRCLK = OutputDevice(27)  #
button = Button(23)

# --- LCD Initialisierung ---
try:
    lcd = CharLCD(i2c_expander='PCF8574', address=I2C_ADDRESS, port=I2C_PORT,
                  cols=16, rows=2, dotsize=8)  #
    lcd.backlight_enabled = True  #
except Exception as e:
    print(f"LCD Fehler: {e}")
    exit()

# --- Matrix Setup (Einzelwuerfel in der Mitte) ---
P = {
    'TL': (0x08, 0xfb), 'TR': (0x08, 0xbf),
    'ML': (0x10, 0xfb), 'MC': (0x10, 0xef), 'MR': (0x10, 0xbf),
    'BL': (0x20, 0xfb), 'BR': (0x20, 0xbf)
}

DICE_PATTERNS = {
    1: [P['MC']],
    2: [P['TL'], P['BR']],
    3: [P['TL'], P['MC'], P['BR']],
    4: [P['TL'], P['TR'], P['BL'], P['BR']],
    5: [P['TL'], P['TR'], P['BL'], P['BR'], P['MC']],
    6: [P['TL'], P['ML'], P['BL'], P['TR'], P['MR'], P['BR']]
}


# --- Hilfsfunktionen ---

def sanitize_text(text):
    """ Ersetzt Umlaute und kuerzt auf 16 Zeichen. """
    replacements = {'ü': 'ue', 'ä': 'ae', 'ö': 'oe', 'ß': 'ss', 'Ü': 'Ue', 'Ä': 'Ae', 'Ö': 'Oe'}
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text[:16]  # Schneidet nach 16 Zeichen hart ab


def lcd_msg(l1, l2=""):
    """ Schreibt Text sicher auf das LCD. """
    l1 = sanitize_text(l1)
    l2 = sanitize_text(l2)
    lcd.clear()  #
    lcd.cursor_pos = (0, 0)  #
    lcd.write_string(l1)  #
    if l2:
        lcd.cursor_pos = (1, 0)  #
        lcd.write_string(l2)  #


def hc595_shift(dat):
    for i in range(8):
        SDI.value = bool(0x80 & (dat << i))  #
        SRCLK.on()  #
        SRCLK.off()  #


def update_matrix(row_data, col_data):
    hc595_shift(col_data)
    hc595_shift(row_data)
    RCLK.on()  #
    sleep(0.0005)
    RCLK.off()


def show_dice(number, duration):
    start_time = time()
    while time() - start_time < duration:
        for row, col in DICE_PATTERNS[number]:
            update_matrix(row, col)
            update_matrix(0x00, 0xff)  # Ghosting verhindern


def roll_animation():
    """ Extra lange und spannende Animation. """
    # 20 Schritte, die immer langsamer werden
    steps = 20
    for i in range(steps):
        duration = 0.05 + (i / steps) ** 2 * 0.5  # Exponentielle Verlangsamung
        num = random.randint(1, 6)
        show_dice(num, duration)

    final = random.randint(1, 6)
    return final


def play_game():
    scores = {1: 0, 2: 0}
    for r in range(1, 4):
        for p in [1, 2]:
            throws = []
            for t in range(1, 3):
                # Kurze Texte um 16 Zeichen nicht zu reissen
                lcd_msg(f"S{p} R{r}/3 W{t}/2", "Bitte Druecken!")
                button.wait_for_press()

                lcd_msg(f"S{p} wuerfelt...", "Viel Glueck!")
                res = roll_animation()
                throws.append(res)

                lcd_msg(f"S{p} Wurf {t}:", f"Zahl {res}")
                show_dice(res, 2.5)

            # Pash Logik
            d1, d2 = throws
            pash = (d1 == d2)
            points = (d1 + d2) * 2 if pash else (d1 + d2)
            scores[p] += points

            status = "!! PASH x2 !!" if pash else f"Punkte: +{points}"
            lcd_msg(f"Spieler {p}", status)
            sleep(3.0)

    # Ende
    winner = "S1 GEWINNT!" if scores[1] > scores[2] else "S2 GEWINNT!"
    if scores[1] == scores[2]: winner = "UNENTSCHIEDEN"

    lcd_msg(winner, f"S1:{scores[1]} S2:{scores[2]}")
    sleep(10)


if __name__ == '__main__':
    try:
        while True:
            lcd_msg("Gambling Dice", "Druck -> Start")
            update_matrix(0x00, 0xff)
            button.wait_for_press()
            play_game()
    except KeyboardInterrupt:
        update_matrix(0x00, 0xff)
        lcd.clear()  #
        lcd.backlight_enabled = False  #
        print("\nBeendet.")