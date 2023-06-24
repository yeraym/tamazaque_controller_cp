import busio
import board
import time
import displayio
import adafruit_imageload
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from adafruit_st7735r import ST7735R

# Release any resources currently in use for the displays
displayio.release_displays()

#spi = board.SPI()
tft_cs = board.D24
tft_dc = board.D25
tft_rst = board.D4

FREQ=60_000_000
spi = busio.SPI(board.SCK, board.MOSI, None)
spi.try_lock()
spi.configure(baudrate=FREQ)
spi.unlock()
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst, baudrate=FREQ)


WIDTH = 160
HEIGHT = 128
ROTATION = 90


display = ST7735R(display_bus, width=WIDTH, height=HEIGHT, rotation=ROTATION, bgr=True, colstart=2, rowstart=1)

display.root_group = None

#font = terminalio.FONT
font = bitmap_font.load_font("/Helvetica-Bold-16.pcf")
font2 = bitmap_font.load_font("/Junction-regular-24.pcf")
color = 0xFFFFFF


from tamazaque.colors import colors
"""
colors = {}
colors["RED"] = (255, 0, 0)
colors["YELLOW"] = (255, 150, 0)
colors["ORANGE"] = (230, 123, 9)
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
"""

def get_color_int(color_name):
    r = colors[color_name][0]
    g = colors[color_name][1]
    b = colors[color_name][2]
    color_int = (((r << 8)+g)<<8)+b
    return color_int

def create_text_label(anchor_x, anchor_y, position_x, position_y, text='label'):
    text_label = label.Label(font, text='', color=color)
    text_label.anchor_point = (anchor_x, anchor_y)
    text_label.anchored_position = (position_x, position_y)
    text_label.text = text
    return text_label


color2 = get_color_int("OLD_LACE")
font2.load_glyphs(b"TMZQ")
msg_group = displayio.Group()
msg_label = label.Label(font2, text='TMZQ', color=color2)
msg_label.anchor_point = (0.5, 0.5)
msg_label.anchored_position = (int(WIDTH/2), int(HEIGHT/2))
msg_group.append(msg_label)

font2.load_glyphs(b"' DFGHIJKLNOPQRSUVWXYabcdefghijklmnopqrstuvwxyz")
font.load_glyphs(b"' ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")


# Make the display context
screen_group = displayio.Group()
display.root_group = screen_group


#image, palette = adafruit_imageload.load("/vulcano_bg4.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
image, palette = adafruit_imageload.load("/vulcano_bg4.png", bitmap=displayio.Bitmap, palette=displayio.Palette)
tile_grid = displayio.TileGrid(image, pixel_shader=palette)
splash_group = displayio.Group()
"""
image_file = open("/vulcano_bg4.bmp", "rb")
image  = displayio.OnDiskBitmap(image_file)
image_sprite  = displayio.TileGrid(image , pixel_shader=getattr(image, 'pixel_shader', displayio.ColorConverter()))
"""
splash_group.append(tile_grid)

screen_group.append(splash_group)
display.refresh(target_frames_per_second=60)

screen_group.append(msg_group)


class Display:
    def __init__(self):
        self.labels = []
        self.timestamp = 0
        self.showing_msg = False
        self.msg_display_time = 0.5

    def init_labels(self, config):
        nr = len(config.data['buttons'])
        nc = len(config.data['buttons'][0])

        label_width = int(WIDTH/nc)
        label_height = int(HEIGHT/nr)

        label_x_offset = int(label_width/2)
        label_y_offset = int(label_height/2)

        self.label_group = displayio.Group()

        self.text_labels = {}
        for i, brow in enumerate(config.data['buttons']):
            for j, b in enumerate(brow):
                posx = (label_width*j)+label_x_offset
                posy = (label_height*i)+label_y_offset
                self.text_labels[b['name']] = create_text_label(0.5, 0.5, posx, posy, b['name'])
                self.label_group.append(self.text_labels[b['name']])
        screen_group.append(self.label_group)


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
        for brow in config.data['buttons']:
            for b in brow:
                label = {}
                label['bname'] = b['name']
                label['text'] = self.get_button_label(config, b['name'])
                color_name = self.get_button_color(config, b['name'])
                label['color'] = get_color_int(color_name)
                self.labels.append(label)
        return self.labels

    def update(self, config, force):
        timestamp = time.monotonic()
        show_labels = False
        if self.showing_msg:
            if (timestamp - self.timestamp) > self.msg_display_time:
                self.showing_msg = False
                msg_label.text = ''
        if show_labels or force:
            self.timestamp = timestamp
            labels = self.get_labels(config)
            self.show_labels()

    def show_msg(self, msg):
        #print('show_msg: ',msg)
        self.timestamp = time.monotonic()
        self.showing_msg = True
        msg_label.text = msg

    def show_labels(self):
        #print('show_labels')
        for l in self.labels:
            #print(l['text'],' ',l['color'])
            self.text_labels[l['bname']].text = l['text']
            self.text_labels[l['bname']].color = l['color']
