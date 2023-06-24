import board
import rotaryio
import digitalio
from adafruit_debouncer import Debouncer

class RotControl:
    def __init__(self, pin1, pin2, pin_sw):
        self.pin1 = pin1
        self.pin2 = pin2
        self.pin_sw = pin_sw
        self.encoder = rotaryio.IncrementalEncoder(self.pin1, self.pin2)
        self.position = self.encoder.position
        self.last_position = self.position

        self.sw = digitalio.DigitalInOut(self.pin_sw)
        self.sw.direction = digitalio.Direction.INPUT
        self.sw.pull = digitalio.Pull.UP
        self.debouncer = Debouncer(self.sw, interval=0.075)
        self.button_pressed = False

        self.update()

    def update(self):
        self.position = self.encoder.position
        self.delta = self.position - self.last_position
        self.last_position = self.position
        self.direction = 0
        if self.delta > 0:
            self.direction = 1
        elif self.delta < 0:
            self.direction = -1

        self.button_pressed = False
        self.debouncer.update()
        if self.debouncer.fell:
            self.button_pressed = True