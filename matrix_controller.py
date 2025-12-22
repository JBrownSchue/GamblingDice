import time
from gpiozero import OutputDevice


class MatrixController:
    def __init__(self, sdi=17, rclk=18, srclk=27):
        # Pins basierend auf Matrix.py
        self.sdi = OutputDevice(sdi)
        self.rclk = OutputDevice(rclk)
        self.srclk = OutputDevice(srclk)

        # Punkt-Definitionen
        p = {
            'TL': (0x08, 0xfb), 'TR': (0x08, 0xbf),
            'ML': (0x10, 0xfb), 'MC': (0x10, 0xef), 'MR': (0x10, 0xbf),
            'BL': (0x20, 0xfb), 'BR': (0x20, 0xbf)
        }
        self.patterns = {
            1: [p['MC']],
            2: [p['TL'], p['BR']],
            3: [p['TL'], p['MC'], p['BR']],
            4: [p['TL'], p['TR'], p['BL'], p['BR']],
            5: [p['TL'], p['TR'], p['BL'], p['BR'], p['MC']],
            6: [p['TL'], p['ML'], p['BL'], p['TR'], p['MR'], p['BR']]
        }

    def _shift(self, row, col):
        for val in [col, row]:
            for i in range(8):
                self.sdi.value = bool(0x80 & (val << i))
                self.srclk.on()
                self.srclk.off()
        self.rclk.on()
        time.sleep(0.0005)
        self.rclk.off()

    def show(self, num, duration):
        start = time.time()
        while time.time() - start < duration:
            for r, c in self.patterns[num]:
                self._shift(r, c)
                self._shift(0, 0xff)

    def clear(self):
        self._shift(0, 0xff)