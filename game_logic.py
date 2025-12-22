import random
import time


class GamblingGame:
    def __init__(self, lcd, matrix, button):
        self.lcd = lcd
        self.matrix = matrix
        self.button = button
        self.scores = {1: 0, 2: 0}

    def roll_animation(self):
        steps = 18
        for i in range(steps):
            duration = 0.05 + (i / steps) ** 2 * 0.4
            num = random.randint(1, 6)
            self.matrix.show(num, duration)
        return random.randint(1, 6)

    def start(self):
        self.scores = {1: 0, 2: 0}
        for r in range(1, 4):
            for p in [1, 2]:
                throws = []
                for t in range(1, 3):
                    self.lcd.display(f"S{p} R{r}/3 W{t}/2", "Bitte Druecken!")
                    self.button.wait_for_press()
                    res = self.roll_animation()
                    throws.append(res)
                    self.lcd.display(f"S{p} Wurf {t}:", f"Zahl {res}")
                    self.matrix.show(res, 2.0)

                pash = (throws[0] == throws[1])
                pts = sum(throws) * (2 if pash else 1)
                self.scores[p] += pts
                self.lcd.display(f"S{p} Runde {r}", "PASH! x2" if pash else f"Score: +{pts}")
                time.sleep(2.5)
        self.show_winner()

    def show_winner(self):
        s1, s2 = self.scores[1], self.scores[2]
        win = "S1 GEWINNT!" if s1 > s2 else "S2 GEWINNT!"
        if s1 == s2: win = "UNENTSCHIEDEN"
        self.lcd.display(win, f"S1:{s1} S2:{s2}")
        time.sleep(10)