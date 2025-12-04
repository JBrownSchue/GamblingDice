from RPLCD.i2c import CharLCD
import time
from gpiozero import OutputDevice

# --- Konfiguration ---
# Dies muss zur Adresse passen, die i2cdetect gefunden hat (0x27)
I2C_ADDRESS = 0x27
I2C_PORT = 1

# --- LCD Initialisierung ---

# Initialisiert das LCD mit der I2C-Adresse 0x27 und Port 1
# Der Zeichensatz ist standardmï¿½ï¿½ig "A00"
lcd = CharLCD(i2c_expander='PCF8574', address=I2C_ADDRESS, port=I2C_PORT,
              cols=16, rows=2, dotsize=8)
print(f"LCD (1602) an Adresse {hex(I2C_ADDRESS)} initialisiert.")


# --- Hauptfunktion ---
def display_hallo_1602():
    # 1. Display lï¿½schen
    lcd.clear()
    # 2. Text auf Zeile 1 (Index 0) und Spalte 0 schreiben
    lcd.cursor_pos = (0, 0)
    lcd.write_string('Hallo Welt!')
    # 3. Text auf Zeile 2 (Index 1) schreiben
    lcd.cursor_pos = (1, 0)
    lcd.write_string('Lets Go')
    print("Text wurde auf dem LCD 1602 angezeigt.")
    time.sleep(5)  # Zeigt den Text fï¿½r 5 Sekunden an


def lcd_clear():
    # 1. Display lï¿½schen
    lcd.clear()
    print("LCD wurde erfolgreich geleert und ausgeschaltet.")
    lcd_power_port.off()


if __name__ == '__main__':
    display_hallo_1602()
    lcd_clear()