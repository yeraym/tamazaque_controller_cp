import board
import time
import displayio
import adafruit_displayio_ssd1306
import busio

#import terminalio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font


displayio.release_displays()
#oled_reset = board.D9
# Use for I2C
#i2c = board.I2C()
i2c = busio.I2C(board.GP7, board.GP6, frequency=400000)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)#, reset=oled_reset)

WIDTH = 128
HEIGHT = 64  # Change to 64 if needed
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

#font = terminalio.FONT
font = bitmap_font.load_font("/Helvetica-Bold-16.pcf")
font2 = bitmap_font.load_font("/Junction-regular-24.pcf")
color = 0xFFFFFF

def create_text_label(anchor_x, anchor_y, position_x, position_y):
    text_label = label.Label(font, text='', max_glyphs=10, color=color)
    text_label.anchor_point = (anchor_x, anchor_y)
    text_label.anchored_position = (position_x, position_y)
    return text_label

text_labels = {}
text_labels['tl'] = create_text_label(0.0, 0.0, 0, 0)
text_labels['tc'] = create_text_label(0.5, 0.0, 64, 0)
text_labels['tr'] = create_text_label(1.0, 0.0, 128, 0)
text_labels['bl'] = create_text_label(0.0, 1.0,0, 64)
text_labels['bc'] = create_text_label(0.5, 1.0, 64, 64)
text_labels['br'] = create_text_label(1.0, 1.0, 128, 64)

label_group = displayio.Group(max_size=10)
label_group.append(text_labels['tl'])
label_group.append(text_labels['tc'])
label_group.append(text_labels['tr'])
label_group.append(text_labels['bl'])
label_group.append(text_labels['bc'])
label_group.append(text_labels['br'])

font2.load_glyphs(b"TAMZQUE")
msg_group = displayio.Group(max_size=10)
msg_label = label.Label(font2, text='TAMAZAQUE', max_glyphs=10, color=color)
msg_label.anchor_point = (0.5, 0.5)
msg_label.anchored_position = (64, 32)
msg_group.append(msg_label)

# Get something on the display as soon as possible by loading
# specific glyphs.
font2.load_glyphs(b"' DFGHIJKLNOPQRSUVWXYabcdefghijklmnopqrstuvwxyz")
font.load_glyphs(b"' ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")

#label_group.hidden = True
#msg_group.hidden = True
# Make the display context
splash = displayio.Group(max_size=10)
display.show(splash)
splash.append(msg_group)
splash.append(label_group)

class Display:
    def __init__(self):
        self.labels = []
        self.timestamp = 0
        self.showing_msg = False
        self.msg_display_time = 0.5

    #def create_label_group(self):

    def get_button_label(self, config, bname):
        bconf = config.get_button(bname)
        if 'label' in bconf:
            return bconf['label']
        elif 'page_state_press' in bconf:
            page_state = config.get_page_state()
            return bconf['page_state_press'][page_state]['label']

    def get_labels(self, config):
        self.labels = []
        for b in config.data['buttons']:
            label = {}
            label['text'] = self.get_button_label(config, b['name'])
            label['position'] = b['position']
            self.labels.append(label)
        return self.labels

    def update(self, config, force):
        timestamp = time.monotonic()
        show_labels = False
        if self.showing_msg:
            if (timestamp - self.timestamp) > self.msg_display_time:
                show_labels = True
                self.showing_msg = False
                msg_label.text = ''
        if show_labels or force:
            self.timestamp = timestamp
            labels = self.get_labels(config)
            self.show_labels()

    def show_msg(self, msg):
        self.timestamp = time.monotonic()
        self.showing_msg = True
        #print('show_msg: '+msg)
        msg_label.text = msg
        #display.show(msg_group)
        #msg_group.hidden = False

    def show_labels(self):
        for l in self.labels:
            text_labels[l['position']].text = l['text']
        #display.show(label_group)
        #msg_group.hidden = True