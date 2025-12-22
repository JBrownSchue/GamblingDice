#!/usr/bin/env python3
from gpiozero import Button
from lcd_controller import LCDController
from matrix_controller import MatrixController
from game_logic import GamblingGame

def main():
    lcd = LCDController()
    matrix = MatrixController()
    button = Button(23)
    game = GamblingGame(lcd, matrix, button)

    try:
        while True:
            lcd.display("Gambling Dice", "Druck -> Start")
            matrix.clear()
            button.wait_for_press()
            game.start()
    except KeyboardInterrupt:
        matrix.clear()
        lcd.off()

if __name__ == "__main__":
    main()