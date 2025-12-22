#!/usr/bin/env python3
import random
from gpiozero import OutputDevice, Button
from time import sleep, time
from RPLCD.i2c import CharLCD

# --- Hardware Setup ---
# LCD (Adresse 0x27)
I2C_ADDRESS = 0x27
I2C_PORT = 1

# Matrix Schieberegister
SDI = OutputDevice(17)
RCLK = OutputDevice(18)
SRCLK = OutputDevice(27)

# Button an GPIO 23
button = Button(23)

# --- LCD Initialisierung ---
try:
    lcd = CharLCD(i2c_expander='PCF8574', address=I2C_ADDRESS, port=I2C_PORT,
                  cols=16, rows=2, dotsize=8)
    lcd.backlight_enabled = True
except Exception as e:
    print(f"LCD Fehler: {e}")
    exit()

# --- Matrix Punkt-Definitionen (Zentrierter Einzelwürfel) ---
# Da eine Reihe kaputt ist, nutzen wir ein kompaktes Muster in der Mitte
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


# --- Funktionen ---

def hc595_shift(dat):
    for i in range(8):
        SDI.value = bool(0x80 & (dat << i))
        SRCLK.on()
        SRCLK.off()


def update_matrix(row_data, col_data):
    hc595_shift(col_data)
    hc595_shift(row_data)
    RCLK.on()
    sleep(0.0005)
    RCLK.off()


def show_dice(number, duration):
    start_time = time()
    while time() - start_time < duration:
        for row, col in DICE_PATTERNS[number]:
            update_matrix(row, col)
            update_matrix(0x00, 0xff)  # Ghosting verhindern


def lcd_msg(l1, l2=""):
    lcd.clear()
    lcd.cursor_pos = (0, 0)
    lcd.write_string(l1)
    if l2:
        lcd.cursor_pos = (1, 0)
        lcd.write_string(l2)


def roll_animation():
    """ Spannendere, längere Animation (ca. 3-4 Sekunden). """
    # Erst schnell, dann immer langsamer für mehr Spannung
    delays = [0.05] * 10 + [0.1] * 5 + [0.2] * 3 + [0.3] * 2 + [0.5] * 1
    for d in delays:
        num = random.randint(1, 6)
        show_dice(num, d)

    final = random.randint(1, 6)
    return final


def play_game():
    scores = {1: 0, 2: 0}
    for r in range(1, 4):  # 3 Runden
        for p in [1, 2]:  # 2 Spieler
            round_throws = []

            for t in range(1, 3):  # 2 Würfe pro Spieler pro Runde
                lcd_msg(f"S{p} Runde {r}/3", f"Wurf {t}/2 - Drueck!")
                button.wait_for_press()

                lcd_msg(f"Spieler {p}...", "Wuerfel rollt!")
                res = roll_animation()
                round_throws.append(res)

                lcd_msg(f"S{p} Wurf {t}: {res}", f"Ergebnis: {res}")
                show_dice(res, 2.0)

            # Auswertung der zwei Würfe
            d1, d2 = round_throws
            is_pash = (d1 == d2)
            points = (d1 + d2) * 2 if is_pash else (d1 + d2)
            scores[p] += points

            msg = "!! PASH x2 !!" if is_pash else f"Summe: {points}"
            lcd_msg(f"S{p} Runde {r} Ende", msg)
            sleep(3.0)

    # Finale
    lcd.clear()
    winner = "S1 GEWINNT!" if scores[1] > scores[2] else "S2 GEWINNT!"
    if scores[1] == scores[2]: winner = "UNENTSCHIEDEN!"

    lcd_msg(winner, f"S1:{scores[1]}  S2:{scores[2]}")
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
        lcd.clear()
        lcd.backlight_enabled = False
        print("\nSpiel beendet.")