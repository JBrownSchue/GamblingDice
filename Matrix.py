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
    print(f"LCD konnte nicht geladen werden: {e}")
    exit()

# --- Matrix Punkt-Definitionen (Geteiltes Display) ---
# Wir definieren Punkte für Würfel 1 (Links) und Würfel 2 (Rechts)
L = {
    'TL': (0x02, 0xfe), 'TR': (0x02, 0xfb),
    'ML': (0x08, 0xfe), 'MC': (0x08, 0xfd), 'MR': (0x08, 0xfb),
    'BL': (0x20, 0xfe), 'BR': (0x20, 0xfb)
}
R = {
    'TL': (0x02, 0xdf), 'TR': (0x02, 0x7f),
    'ML': (0x08, 0xdf), 'MC': (0x08, 0xbf), 'MR': (0x08, 0x7f),
    'BL': (0x20, 0xdf), 'BR': (0x20, 0x7f)
}


def get_pattern(side_map, num):
    if num == 1: return [side_map['MC']]
    if num == 2: return [side_map['TL'], side_map['BR']]
    if num == 3: return [side_map['TL'], side_map['MC'], side_map['BR']]
    if num == 4: return [side_map['TL'], side_map['TR'], side_map['BL'], side_map['BR']]
    if num == 5: return [side_map['TL'], side_map['TR'], side_map['BL'], side_map['BR'], side_map['MC']]
    if num == 6: return [side_map['TL'], side_map['ML'], side_map['BL'], side_map['TR'], side_map['MR'], side_map['BR']]
    return []


# --- Hilfsfunktionen ---

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


def show_two_dice(n1, n2, duration):
    """ Zeichnet beide Würfel gleichzeitig auf die Matrix (Multiplexing). """
    points = get_pattern(L, n1) + get_pattern(R, n2)
    start_time = time()
    while time() - start_time < duration:
        for row, col in points:
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
    """ Simuliert das Rollen von zwei Würfeln. """
    for speed in [0.1, 0.1, 0.15, 0.2, 0.3]:
        show_two_dice(random.randint(1, 6), random.randint(1, 6), speed)
    d1, d2 = random.randint(1, 6), random.randint(1, 6)
    return d1, d2


def play_game():
    scores = {1: 0, 2: 0}
    for r in range(1, 4):
        for p in [1, 2]:
            lcd_msg(f"Spieler {p}!", f"Runde {r}/3 - Drueck!")
            button.wait_for_press()

            d1, d2 = roll_animation()
            sum_dice = d1 + d2
            is_pash = (d1 == d2)

            # Punkteberechnung mit Pash-Regel
            round_score = sum_dice * 2 if is_pash else sum_dice
            scores[p] += round_score

            # Feedback
            pash_txt = " !! PASH !!" if is_pash else ""
            lcd_msg(f"P{p}: {d1}+{d2}={round_score}", f"Gesamt: {scores[p]}{pash_txt}")
            show_two_dice(d1, d2, 4.0)

    # Finale Auswertung
    winner = "S1 GEWINNT!" if scores[1] > scores[2] else "S2 GEWINNT!"
    if scores[1] == scores[2]: winner = "UNENTSCHIEDEN!"

    lcd_msg(winner, f"S1:{scores[1]}  S2:{scores[2]}")
    sleep(10)


if __name__ == '__main__':
    try:
        while True:
            lcd_msg("Gambling Dice", "Press to start!")
            update_matrix(0x00, 0xff)
            button.wait_for_press()
            play_game()
    except KeyboardInterrupt:
        update_matrix(0x00, 0xff)
        lcd.clear()
        lcd.backlight_enabled = False
        print("\nSpiel beendet.")