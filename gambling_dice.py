#!/usr/bin/env python3
import random
import time
from gpiozero import OutputDevice, Button
from RPLCD.i2c import CharLCD


class GamblingDice:
    def __init__(self):
        # Hardware Setup
        self.lcd = CharLCD('PCF8574', 0x27, port=1, cols=16, rows=2)
        self.sdi = OutputDevice(17)
        self.rclk = OutputDevice(18)
        self.srclk = OutputDevice(27)
        self.button = Button(23)

        # Matrix Patterns
        self.p = {
            'TL': (0x08, 0xfb), 'TR': (0x08, 0xbf),
            'ML': (0x10, 0xfb), 'MC': (0x10, 0xef), 'MR': (0x10, 0xbf),
            'BL': (0x20, 0xfb), 'BR': (0x20, 0xbf)
        }
        self.patterns = {
            1: [self.p['MC']],
            2: [self.p['TL'], self.p['BR']],
            3: [self.p['TL'], self.p['MC'], self.p['BR']],
            4: [self.p['TL'], self.p['TR'], self.p['BL'], self.p['BR']],
            5: [self.p['TL'], self.p['TR'], self.p['BL'], self.p['BR'], self.p['MC']],
            6: [self.p['TL'], self.p['ML'], self.p['BL'], self.p['TR'], self.p['MR'], self.p['BR']]
        }

    def lcd_msg(self, l1, l2=""):
        # Umlaute fixen & kuerzen
        def clean(t):
            for c, r in {'ü': 'ue', 'ä': 'ae', 'ö': 'oe', 'ß': 'ss'}.items(): t = t.replace(c, r)
            return t[:16]

        self.lcd.clear()
        self.lcd.cursor_pos = (0, 0)
        self.lcd.write_string(clean(l1))
        if l2:
            self.lcd.cursor_pos = (1, 0)
            self.lcd.write_string(clean(l2))

    def update_matrix(self, row, col):
        # 8-Bit Shift
        for i in range(8):
            self.sdi.value = bool(0x80 & (col << i))
            self.srclk.on()
            self.srclk.off()
        for i in range(8):
            self.sdi.value = bool(0x80 & (row << i))
            self.srclk.on()
            self.srclk.off()
        self.rclk.on()
        time.sleep(0.0005)
        self.rclk.off()

    def show_dice(self, num, duration):
        start = time.time()
        while time.time() - start < duration:
            for r, c in self.patterns[num]:
                self.update_matrix(r, c)
                self.update_matrix(0, 0xff)

    def roll(self):
        for i in range(18):
            d = 0.05 + (i / 18) ** 2 * 0.4
            n = random.randint(1, 6)
            self.show_dice(n, d)
        return random.randint(1, 6)

    def play(self):
        scores = {1: 0, 2: 0}
        for r in range(1, 4):
            for p in [1, 2]:
                throws = []
                for t in range(1, 3):
                    self.lcd_msg(f"S{p} R{r}/3 W{t}/2", "Bitte Druecken!")
                    self.button.wait_for_press()
                    res = self.roll()
                    throws.append(res)
                    self.lcd_msg(f"S{p} Wurf {t}:", f"Zahl {res}")
                    self.show_dice(res, 2.0)

                # Punkte & Pash
                pash = throws[0] == throws[1]
                pts = sum(throws) * (2 if pash else 1)
                scores[p] += pts
                self.lcd_msg(f"S{p} Runde {r}", "PASH! x2" if pash else f"Score: +{pts}")
                time.sleep(2.5)

        # Finale
        win = "S1 GEWINNT!" if scores[1] > scores[2] else "S2 GEWINNT!"
        if scores[1] == scores[2]: win = "UNENTSCHIEDEN"
        self.lcd_msg(win, f"S1:{scores[1]} S2:{scores[2]}")
        time.sleep(10)


if __name__ == "__main__":
    game = GamblingDice()
    try:
        while True:
            game.lcd_msg("Gambling Dice", "Druck -> Start")
            game.update_matrix(0, 0xff)
            game.button.wait_for_press()
            game.play()
    except KeyboardInterrupt:
        game.update_matrix(0, 0xff)
        game.lcd.clear()
        game.lcd.backlight_enabled = False