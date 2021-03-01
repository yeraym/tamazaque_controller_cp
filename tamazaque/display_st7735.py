import busio
import board
import time
import displayio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from adafruit_st7735r import ST7735R

# Release any resources currently in use for the displays
displayio.release_displays()

#spi = board.SPI()
tft_cs = board.GP13
tft_dc = board.GP9
tft_rst = board.GP8

spi_clk = board.GP10
spi_mosi = board.GP11


spi = busio.SPI(spi_clk, MOSI=spi_mosi)
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst)


WIDTH = 160
HEIGHT = 128
ROTATION = 90


display = ST7735R(display_bus, width=WIDTH, height=HEIGHT, rotation=ROTATION, bgr=True, colstart=2, rowstart=1)

#font = terminalio.FONT
font = bitmap_font.load_font("/Helvetica-Bold-16.pcf")
font2 = bitmap_font.load_font("/Junction-regular-24.pcf")
color = 0xFFFFFF


def create_text_label(anchor_x, anchor_y, position_x, position_y, text='label'):
    text_label = label.Label(font, text='', max_glyphs=10, color=color)
    text_label.anchor_point = (anchor_x, anchor_y)
    text_label.anchored_position = (position_x, position_y)
    text_label.text = text
    return text_label

text_labels = {}
text_labels['tl'] = create_text_label(0.0, 0.0, 0, 0)
text_labels['tc'] = create_text_label(0.5, 0.0, int(WIDTH/2), 0)
text_labels['tr'] = create_text_label(1.0, 0.0, WIDTH, 0)
text_labels['bl'] = create_text_label(0.0, 1.0,0, HEIGHT)
text_labels['bc'] = create_text_label(0.5, 1.0, int(WIDTH/2), HEIGHT)
text_labels['br'] = create_text_label(1.0, 1.0, WIDTH, HEIGHT)

label_group = displayio.Group(max_size=10)
label_group.append(text_labels['tl'])
label_group.append(text_labels['tc'])
label_group.append(text_labels['tr'])
label_group.append(text_labels['bl'])
label_group.append(text_labels['bc'])
label_group.append(text_labels['br'])


colors = {}
colors["RED"] = (255, 0, 0)
colors["YELLOW"] = (255, 150, 0)
colors["ORANGE"] = (255, 40, 0)
colors["GREEN"] = (0, 255, 0)
colors["TEAL"] = (0, 255, 120)
colors["CYAN"] = (0, 255, 255)
colors["BLUE"] = (0, 0, 255)
colors["PURPLE"] = (180, 0, 255)
colors["MAGENTA"] = (255, 0, 20)
colors["WHITE"] = (255, 255, 255)
colors["BLACK"] = (0, 0, 0)
colors["GOLD"] = (255, 222, 30)
colors["PINK"] = (242, 90, 255)
colors["AQUA"] = (50, 255, 255)
colors["JADE"] = (0, 255, 40)
colors["AMBER"] = (255, 100, 0)
colors["OLD_LACE"] = (253, 245, 230)

def get_color_int(color_name):
    r = colors[color_name][0]
    g = colors[color_name][1]
    b = colors[color_name][2]
    color_int = (((r << 8)+g)<<8)+b
    return color_int

color2 = get_color_int("OLD_LACE")
font2.load_glyphs(b"TAMZQUE")
msg_group = displayio.Group(max_size=10)
msg_label = label.Label(font2, text='TAMAZAQUE', max_glyphs=10, color=color2)
msg_label.anchor_point = (0.5, 0.5)
msg_label.anchored_position = (int(WIDTH/2), int(HEIGHT/2))
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

    def get_button_color(self, config, bname):
        bconf = config.get_button(bname)
        if 'led_color' in bconf:
            return bconf['led_color']
        elif 'page_state_press' in bconf:
            page_state = config.get_page_state()
            return bconf['page_state_press'][page_state]['led_color']
        elif 'state_press' in bconf:
            bstate = config.get_button_state(bname)
            return bconf['state_press'][bstate]['led_color']
        return "BLACK"

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
            color_name = self.get_button_color(config, b['name'])
            label['color'] = get_color_int(color_name)
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
            text_labels[l['position']].color = l['color']
        #display.show(label_group)
        #msg_group.hidden = True