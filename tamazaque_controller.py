import board
import busio

# early initialize UART
uart = busio.UART(tx=board.TX, rx=None, baudrate=31250, timeout=0.001)

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
#import tamazaque.display_st7735
import tamazaque.dynamic_display_st7735
import tamazaque.leds


config_file = open('config.json','r')
myconfig = json.load(config_file)

config = tamazaque.config.Config(myconfig)
button_controller = tamazaque.buttons.Buttons()
#display = tamazaque.display.Display()
#display = tamazaque.display_st7735.Display()
display = tamazaque.dynamic_display_st7735.Display()

# Initialize buttons from config
for brow in config.data['buttons']:
    for b in brow:
        button_controller.add_button(b['name'],b['pin'])

# Display labels for buttons
display.init_labels(config)
display.update(config, True)

# Initialize leds for buttons
leds = tamazaque.leds.Leds(len(button_controller.states), board.SDA)
leds.update(config)

# Initialize midi output
midi_channel = 1
midi_usb = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=midi_channel-1)

midi_uart = adafruit_midi.MIDI(midi_out=uart, out_channel=midi_channel-1)


# rotary control
import tamazaque.rotcontrol
control = tamazaque.rotcontrol.RotControl(board.A2,board.A3,board.MISO)
control.update()

# Initialize expression input
import tamazaque.expression
exps = {}
for exp in config.data['expression']:
    exps[exp['name']] = tamazaque.expression.Expression(getattr(board,exp['pin']), min_input=1500, max_input=62000, min_output=0, max_output=127, activate_threshold=10, alpha=0.8)



def send_midi_uart(msg, channel=0):
    if isinstance(msg, MIDIMessage):
        #msg.channel = channel
        data = msg.__bytes__()  # bytes(object) does not work in uPy
        #print("sending uart: ",data)
        uart.write(data)

def send_midi(midi_action):
    #print('command:',midi_action['command'],' control:',midi_action['control'],' value:',midi_action['value'])
    if midi_action['command']=='CC':
        #print('sending midi')
        cc_msg = ControlChange(midi_action['control'], midi_action['value'], channel=midi_channel-1)
        #midi.send(ControlChange(midi_action['control'], midi_action['value']))
        midi_usb.send(cc_msg)
        #send_midi_uart(cc_msg)
        midi_uart.send(cc_msg)

def run_action(action, update_leds=True):
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
        display.update(config, True)
        if update_leds:
            leds.update(config)

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
            run_action(state_action, update_leds=False)
            config.set_button_state(bname,state_action['to_state'])
            leds.update(config)
            display.update(config, True)


        action_page_state_press = config.get_button_action(bname,'page_state_press')
        if action_page_state_press:
            page_state_action = config.get_button_page_state_action(bname)
            run_action(page_state_action, update_leds=False)
            config.set_page_state(page_state_action['to_page_state'])
            leds.update(config)
            display.update(config, True)


def process_exp_even(exp_name,state):
    if state.activate:
        action = config.get_expression_action(exp_name,'activate')
        if action:
            run_action(action)
    elif state.deactivate:
        action = config.get_expression_action(exp_name,'deactivate')
        if action:
            run_action(action)

    if not state.is_down:
        action = config.get_expression_action(exp_name,'change')
        if action:
            action['midi'][0]['value'] = state.v
            run_action(action)


import tamazaque.menu
menu = tamazaque.menu.Menu()

def stat(lbl):
    print('%s %g' % (lbl, gc.mem_free() / 1024))

#stat('mainloop')

gc.collect()

# Main loop
leds.update(config)

timestamp = time.monotonic()
last_timestamp = timestamp
while True:

    # update dispay every 0.5 seconds to clear msg
    timestamp = time.monotonic()
    if (timestamp - last_timestamp) > 0.5:
        last_timestamp = timestamp
        if display.showing_msg:
            display.update(config, False)

    control.update()
    if control.button_pressed:
        print("control pressed")
        leds.update(config)
        menu.list_configs()
    if control.direction == 1:
        config.page_down()
        display.update(config, True)
        leds.update(config)
    elif control.direction == -1:
        config.page_up()
        display.update(config, True)
        leds.update(config)

    """
    for expname in exps:
        exp = exps[expname]
        v = exp.update()
        process_exp_even(expname, exp)

        if exp.activate:
            print('up')
        if exp.deactivate:
            print('down')
        if not exp.is_down:
            print("{} {} {} {} {} {}".format(v, exp.x, exp.s1,exp.s2,exp.a,exp.b))
    """

    button_controller.update()


    for bname in button_controller.states:
        state = button_controller.states[bname]
        #display.update(config, False)

        if state['changed']:
            #stat('button event')
            #print(bname,' ',state['event'],' ',state['special_event'],' ',state['press_timestamp'],' ',state['release_timestamp'])
            process_button_event(bname,state)
            gc.collect()
            #stat('button event post')
