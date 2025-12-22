from RPLCD.i2c import CharLCD

class LCDController:
    def __init__(self, address=0x27, port=1):
        # Initialisierung basierend auf LCD.py
        self.lcd = CharLCD('PCF8574', address, port=port, cols=16, rows=2)
        self.lcd.backlight_enabled = True

    def _sanitize(self, text):
        replacements = {'ü':'ue','ä':'ae','ö':'oe','ß':'ss'}
        for c, r in replacements.items():
            text = text.replace(c, r)
        return text[:16]

    def display(self, line1, line2=""):
        self.lcd.clear()
        self.lcd.cursor_pos = (0, 0)
        self.lcd.write_string(self._sanitize(line1))
        if line2:
            self.lcd.cursor_pos = (1, 0)
            self.lcd.write_string(self._sanitize(line2))

    def off(self):
        self.lcd.clear()
        self.lcd.backlight_enabled = False