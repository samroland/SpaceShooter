from colorsys import hsv_to_rgb
import numpy as np

class Color():
    def __init__(self, h,s,v,a=1.0):
        self.hsv = (h,s,v)
        self.rgb = self.hsv_to_rgb(self.hsv)
        self.set_alpha(a)
        return

    def hsv_to_rgb(self, hsv):
        hsv_1 = np.array(hsv_to_rgb(*hsv))
        hsv_255 = (255*hsv_1).astype(int)
        return tuple(hsv_255)

    def set_alpha(self, alpha):
        if isinstance(alpha, float):
            alpha = int(255*alpha)
        self.rgba = self.rgb + (alpha,)
        return

white = Color(0.0, 0.0, 1.0)
black = Color(0.0, 0.0, 0.0)
dark_gray = Color(0.0, 0.0, 0.1)