import board
import digitalio
import time
from adafruit_debouncer import Debouncer


class Buttons:
    def __init__(self):
        self.debouncers = {}
        self.states = {}
        self.debounce_interval = 0.075
        self.double_press_interval = 0.5
        self.long_press_interval = 1

    def add_button(self, button_name, pin_name):
        io = digitalio.DigitalInOut(getattr(board,pin_name))
        io.direction = digitalio.Direction.INPUT
        io.pull = digitalio.Pull.UP
        self.debouncers[button_name] = Debouncer(io, interval=self.debounce_interval)
        self.states[button_name] = {'pin_name': pin_name, 'value':'up', 'changed':False, 'event':'', 'press_timestamp':0, 'release_timestamp':0, 'special_event':''}

    def update(self):
        for button_name in self.states:
            state = self.states[button_name]
            debouncer = self.debouncers[button_name]
            debouncer.update()
            state['changed'] = False
            timestamp = time.monotonic()
            if debouncer.fell:
                state['event'] = 'press'
                state['value'] = 'down'
                state['changed'] = True
                state['special_event'] = ''
                if timestamp - state['press_timestamp'] < self.double_press_interval:
                    state['special_event'] = 'double_press'
                state['press_timestamp'] = timestamp
            if debouncer.rose:
                state['event'] = 'release'
                state['value'] = 'up'
                state['changed'] = True
                state['special_event'] = ''
                if timestamp - state['press_timestamp'] > self.long_press_interval:
                    state['special_event'] = 'long_press'
                state['release_timestamp'] = timestamp

