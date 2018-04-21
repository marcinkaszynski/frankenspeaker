import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import alsaaudio
import time

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


class Vis(object):
    def __init__(self):
        self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=None)
        self.disp.begin()

        self.image = Image.new('1', (self.disp.width, self.disp.height))
        self.font = ImageFont.load_default()

        self.volume = None
        self.max_volume = 100
        self.dirty = False

    def set_volume(self, volume):
        print("SV", self.volume, volume)
        if self.volume != volume:
            self.dirty = True
            self.volume = volume

    def update_display(self, ts):
        if not self.dirty:
            return

        draw = ImageDraw.Draw(self.image)
        draw.rectangle((0, 0, self.disp.width-1, self.disp.height-1), outline=0, fill=0)
        draw.text((0, 0), '%d / %d' % (self.volume, self.max_volume), font=self.font, fill=255)
        self.disp.image(self.image)
        self.disp.display()
        self.dirty = False


def main_loop():
    vis = Vis()
    while True:
        # Don't care about stereo, we'll even levels on first volume
        # change anyway.
        mixer = alsaaudio.Mixer('Speaker')
        vis.set_volume(max(mixer.getvolume()))

        ts = time.time()
        vis.update_display(ts)
        time.sleep(0.1)

if __name__ == '__main__':
    main_loop()
