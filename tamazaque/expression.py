import time
import board
import analogio

"""
import tamazaque.expression

exp = tamazaque.expression.Expression(board.A1)

while True:
    v = exp.update()
    if exp.activate:
        print('up')

    if exp.deactivate:
        print('down')

    if not exp.is_down:
        print(v)

    time.sleep(0.01)
"""

def map_range(x, in_min, in_max, out_min, out_max):
    """
    Maps a number from one range to another.
    Note: This implementation handles values < in_min differently than arduino's map function does.

    :return: Returns value mapped to new range
    :rtype: float
    """
    in_range = in_max - in_min
    in_delta = x - in_min
    if in_range != 0:
        mapped = in_delta / in_range
    elif in_delta != 0:
        mapped = in_delta
    else:
        mapped = 0.5
    mapped *= out_max - out_min
    mapped += out_min
    if out_min <= out_max:
        return max(min(mapped, out_max), out_min)
    return min(max(mapped, out_max), out_min)

class Expression:
    def __init__(self, pin, min_input=500, max_input=62000, min_output=0, max_output=127, activate_threshold=10, alpha=0.8):
        self.pin = analogio.AnalogIn(pin)
        self.x = self.pin.value

        self.s1 = self.x
        self.s2 = self.x
        self.alpha = alpha

        self.last_down = time.monotonic()
        self.last_up = time.monotonic()
        self.is_down = True

        self.activate = False
        self.deactivate = False

        self.min_input = min_input
        self.max_input = max_input
        self.min_output = min_output
        self.max_output = max_output

        self.activate_threshold = activate_threshold

        self.v = map_range(self.x, self.min_input, self.max_input, self.min_output, self.max_output)



    def update(self):
        #double exponential filter
        self.x = self.pin.value
        self.s1 = (self.alpha*self.x) + (1-self.alpha)*self.s1
        self.s2 = (self.alpha*self.s1) + (1-self.alpha)*self.s2

        #smooth value
        self.a = 2*self.s1 - self.s2
        #trend
        self.b = (self.alpha/(1-self.alpha))*(self.s1-self.s2)

        #print("{} {} {} {} {}".format(x,s1,s2,a,b))
        #print("{} \t{} \t{}".format(x,int(a),int(b)))

        #map input -> output
        self.v = map_range(self.a, self.min_input, self.max_input, self.min_output, self.max_output)
        self.v = int(self.v)

        #if not self.is_down:
        #    print(a, v)

        self.activate = False
        self.deactivate = False

        if self.v<self.activate_threshold:
            self.last_down = time.monotonic()
            if not self.is_down:
                if self.last_down-self.last_up>0.3:
                    self.is_down = True
                    self.deactivate = True
        else:
            self.last_up = time.monotonic()
            if self.is_down:
                if self.last_up-self.last_down>0.3:
                    self.is_down = False
                    self.activate = True

        return self.v