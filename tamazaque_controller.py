import board
import busio
uart = busio.UART(tx=board.GP0, rx=None, baudrate=31250)#, timeout=0.001)

import gc
import time
import json

import usb_midi
import adafruit_midi
from adafruit_midi.control_change import ControlChange
from adafruit_midi import MIDIMessage

import tamazaque.config
import tamazaque.buttons
#import tamazaque.display
import tamazaque.display_st7735
import tamazaque.leds

config_file = open('config.json','r')
myconfig = json.load(config_file)

config = tamazaque.config.Config(myconfig)
button_controller = tamazaque.buttons.Buttons()
#display = tamazaque.display.Display()
display = tamazaque.display_st7735.Display()


for b in config.data['buttons']:
    button_controller.add_button(b['name'],b['pin'])

display.update(config, True)

leds = tamazaque.leds.Leds(len(config.data['buttons']), board.GP5)
leds.update(config)

midi_channel = 1
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=midi_channel-1)

def send_midi_uart(msg, channel=0):
    if isinstance(msg, MIDIMessage):
        msg.channel = channel
        data = msg.__bytes__()  # bytes(object) does not work in uPy
        #print("sending uart: ",data)
        uart.write(data)

def send_midi(midi_action):
    #print('command:',midi_action['command'],' control:',midi_action['control'],' value:',midi_action['value'])
    if midi_action['command']=='CC':
        #print('sending midi')
        cc_msg = ControlChange(midi_action['control'], midi_action['value'])
        #midi.send(ControlChange(midi_action['control'], midi_action['value']))
        midi.send(cc_msg)
        send_midi_uart(cc_msg)

def run_action(action):
    #print(action['msg'])
    display.show_msg(action['msg'])
    if 'midi' in action:
        for midi_action in action['midi']:
            #print(midi_action)
            send_midi(midi_action)
    if 'control' in action:
        control_action = action['control']
        #print(control_action)
        config.control_action(control_action)

def process_button_event(bname,state):
    event = state['event']
    action = config.get_button_action(bname,event)
    special_action = config.get_button_action(bname,state['special_event'])
    if special_action:
        run_action(special_action)

    if action:
        run_action(action)

    if event=='press':
        action_state_press = config.get_button_action(bname,'state_press')
        if action_state_press:
            state_action = config.get_button_state_action(bname)
            run_action(state_action)
            config.set_button_state(bname,state_action['to_state'])

        action_page_state_press = config.get_button_action(bname,'page_state_press')
        if action_page_state_press:
            page_state_action = config.get_button_page_state_action(bname)
            run_action(page_state_action)
            config.set_page_state(page_state_action['to_page_state'])

gc.collect()

while True:
    button_controller.update()
    for bname in button_controller.states:
        state = button_controller.states[bname]
        display.update(config, False)

        if state['changed']:
            #print(bname,' ',state['event'],' ',state['special_event'],' ',state['press_timestamp'],' ',state['release_timestamp'])
            process_button_event(bname,state)
            leds.update(config)