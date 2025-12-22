#!/usr/bin/env python3
import random
from gpiozero import OutputDevice, Button
from time import sleep, time
from RPLCD.i2c import CharLCD

# --- Konfiguration Hardware ---
# LCD
I2C_ADDRESS = 0x27
I2C_PORT = 1

# Schieberegister Matrix
SDI = OutputDevice(17)
RCLK = OutputDevice(18)
SRCLK = OutputDevice(27)

# Button an GPIO 23
button = Button(23)

# --- Initialisierung ---
try:
    lcd = CharLCD(i2c_expander='PCF8574', address=I2C_ADDRESS, port=I2C_PORT,
                  cols=16, rows=2, dotsize=8)
    lcd.backlight_enabled = True
except Exception as e:
    print(f"LCD Fehler: {e}")
    exit()

# Punkt-Definitionen für die Matrix (wie zuvor)
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


def show_dice_on_matrix(number, duration):
    start_time = time()
    while time() - start_time < duration:
        for row, col in DICE_PATTERNS[number]:
            update_matrix(row, col)
            update_matrix(0x00, 0xff)


def lcd_msg(line1, line2=""):
    lcd.clear()
    lcd.cursor_pos = (0, 0)
    lcd.write_string(line1)
    if line2:
        lcd.cursor_pos = (1, 0)
        lcd.write_string(line2)


def roll_animation():
    """ Spielt die Animation und gibt eine Zufallszahl zurück. """
    for speed in [0.1, 0.1, 0.15, 0.2, 0.3]:
        num = random.randint(1, 6)
        show_dice_on_matrix(num, speed)
    final = random.randint(1, 6)
    return final


def play_game():
    scores = {1: 0, 2: 0}
    max_rounds = 3

    for round_num in range(1, max_rounds + 1):
        for player in [1, 2]:
            lcd_msg(f"Spieler {player} Drueck!", f"Runde {round_num}/{max_rounds}")
            print(f"Spieler {player} ist am Zug...")

            # Warten auf Button-Druck
            button.wait_for_press()

            # Würfeln
            lcd_msg(f"Spieler {player}...", "Wuerfelt!")
            result = roll_animation()
            scores[player] += result

            # Ergebnis anzeigen
            lcd_msg(f"P{player} warf: {result}", f"Gesamt: {scores[player]}")
            show_dice_on_matrix(result, 3.0)  # 3 Sek das Ergebnis auf Matrix lassen

    # Spielende: Auswertung
    lcd.clear()
    if scores[1] > scores[2]:
        winner_text = "S1 GEWINNT!"
    elif scores[2] > scores[1]:
        winner_text = "S2 GEWINNT!"
    else:
        winner_text = "UNENTSCHIEDEN!"

    lcd_msg(winner_text, f"S1:{scores[1]}  S2:{scores[2]}")
    print(f"Endergebnis: {winner_text} (S1: {scores[1]} | S2: {scores[2]})")
    sleep(10)  # 10 Sekunden das Endergebnis zeigen


def main():
    while True:
        lcd_msg("Gambling Dice", "Button -> Start")
        update_matrix(0x00, 0xff)
        button.wait_for_press()
        play_game()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        update_matrix(0x00, 0xff)
        lcd.clear()
        lcd.backlight_enabled = False
        print("\nSpiel beendet.")