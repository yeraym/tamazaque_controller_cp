import board
import neopixel
import time


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

class Leds:
    def __init__(self,num_pixels, pixel_pin, brightness=0.05):
        self.num_pixels = num_pixels
        self.pixel_pin = pixel_pin
        self.brightness = brightness
        self.pixels = neopixel.NeoPixel(self.pixel_pin, self.num_pixels, brightness=self.brightness, auto_write=False)

    def led_color(self, position, color):
        self.pixels[position] = colors[color]
        self.pixels.show()

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

    def update(self, config):
        for b in config.data['buttons']:
            pos = b["led_position"]
            color = self.get_button_color(config, b['name'])
            self.pixels[pos] = colors[color]
        self.pixels.show()