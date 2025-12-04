from RPLCD.i2c import CharLCD
import time

# --- Konfiguration ---
I2C_ADDRESS = 0x27  # Das haben wir vorhin gefunden
I2C_PORT = 1

# --- LCD Initialisierung ---
try:
    print(f"Initialisiere LCD an Adresse {hex(I2C_ADDRESS)}...")
    lcd = CharLCD(i2c_expander='PCF8574', address=I2C_ADDRESS, port=I2C_PORT,
                  cols=16, rows=2, dotsize=8)

    # Backlight explizit anschalten
    lcd.backlight_enabled = True

except Exception as e:
    print(f"Fehler beim Verbinden: {e}")
    print("Ist das Display korrekt verkabelt?")
    exit()


# --- Hauptfunktion ---
def main():
    # 1. Display leeren
    lcd.clear()

    # 2. Text schreiben
    lcd.cursor_pos = (0, 0)
    lcd.write_string('Es klappt!')

    lcd.cursor_pos = (1, 0)
    lcd.write_string('Hallo Justin')

    print("Text wurde auf dem Display angezeigt.")
    print("Drücke Strg+C um zu beenden.")

    # Endlosschleife damit das Skript läuft
    while True:
        time.sleep(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        # Sauber beenden bei Strg+C
        lcd.clear()
        lcd.backlight_enabled = False
        print("\nProgramm beendet.")