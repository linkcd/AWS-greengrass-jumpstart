import sys
import time
import random

from sense_hat import SenseHat
sense = SenseHat()

number = str(sys.argv[1])

try:
    while True:
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

        sense.show_letter(number, text_colour=[r,g,b])
        time.sleep(1)
finally:
    print("led.py finished!")
    sense.clear()
