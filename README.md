# Tamazaque, json configurable midi controller built with CircuitPython

Tamazaque is a pedal midi controller that sends midi messages over usb. The main feature is the json configuration file. This file defines the number of buttons and their GPIO pins, it also contains the midi messages associated with each button. Each button can send multiple midi messages in each of these events: press, release and long press. The configuration support multiple configuration pages, with each page containing new set of messages associated to the buttons, there is also an internal command to change the active page, this command can be fired by any button event.

![tmzq_midi_controller](https://github.com/yeraym/tamazaque_controller_cp/assets/15657/b1c3af25-ba16-49cc-abce-f1358898b884)

You can use it with just a CircuitPython board and some buttons connected to the GPIO pins to send midi commands over usb.

![minimal](https://github.com/yeraym/tamazaque_controller_cp/assets/15657/907af6a1-58a6-47bb-a605-386d458833be)

I have built it to use as a pedal midi controller with the following features that are optional, you can modify tamzaque_controller.py to disabled them:

* OLED screen
* 8 rgb neoleds
* 1 clickable rotary controller
* Internal battery
* DIN midi output
* Expresession pedal input (work in progress)

## Flexible configuration

* Multiple configuration pages in the same file
* Multiple midi commands in each event
* Press, long press and release events
* Button state events: Pressing the button changes its state, each state has its own midi commands, button label and led color
* Page state events: Pressing a button can change the page state, in each page state the selected buttons have its own midi commands, button label and led color


https://github.com/yeraym/tamazaque_controller_cp/assets/15657/9300e179-c97f-4f25-ac0f-a5f47503e1b4



### Controlling Helix looper with page states


https://github.com/yeraym/tamazaque_controller_cp/assets/15657/437ce06c-3e69-4787-ad2f-32ee27311f39

With two buttons and three states we have this state diagram

```mermaid
stateDiagram-v2
    stop: Stopped
    rec: Recording
    play: Playing
    stop --> rec: b2 REC
    rec --> rec: b2 OVR
    play --> rec: b2 OVR
    stop --> play: b1 PLA
    rec --> play: b1 PLA
    play --> stop: b1 STP
```


The page state remains between page chanes.

https://github.com/yeraym/tamazaque_controller_cp/assets/15657/d9d0d5d9-dbfc-4f12-8cac-32a77c226c4c




## Hardware

I built it with an Adafruit Feather RP2040 borad.

![tmzq_midi_controller_inside](https://github.com/yeraym/tamazaque_controller_cp/assets/15657/5aabd8ad-6b75-4e17-8656-d9592093e974)

![tmzq_midi_controller_io](https://github.com/yeraym/tamazaque_controller_cp/assets/15657/e0eda75c-3e58-4662-8031-2d162cbce885)

![tmzq_midi_controller_usb](https://github.com/yeraym/tamazaque_controller_cp/assets/15657/05ef5818-a3ea-4289-bcc9-b890bbc8eead)

### Build

I built a little carrier with some male-female long headers and a spot prototyping board to be able to swap the feather with any other compatible one.

![carrier](https://github.com/yeraym/tamazaque_controller_cp/assets/15657/01021ad3-de39-4b57-b331-2e723bf25959)

You can see in the backside it has two rows which I use for ground a +V connections.

![carrier_back](https://github.com/yeraym/tamazaque_controller_cp/assets/15657/89d84c2a-a986-4466-9453-3f676f7910ef)


 ## Software
 
 Adafruit CircuitPython 8.0.5 on 2023-03-31
