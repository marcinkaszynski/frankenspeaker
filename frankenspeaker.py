import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import RPi.GPIO as GPIO
import alsaaudio
import time

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


MAX_VOL = 100
MIN_VOL = 0


class Vis(object):
    def __init__(self):
        self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=None)
        self.disp.begin()

        self.image = Image.new('1', (self.disp.width, self.disp.height))
        self.font = ImageFont.load_default()

        self.volume = None
        self.dirty = False

    def set_volume(self, volume):
        if self.volume != volume:
            self.dirty = True
            self.volume = volume

    def update_display(self, ts):
        if not self.dirty:
            return

        draw = ImageDraw.Draw(self.image)
        draw.rectangle((0, 0, self.disp.width-1, self.disp.height-1), outline=0, fill=0)
        draw.text((0, 0), '%d / %d' % (self.volume, MAX_VOL), font=self.font, fill=255)
        self.disp.image(self.image)
        self.disp.display()
        self.dirty = False


class Buttons(object):
    def __init__(self, vol_dn, vol_up):
        self.last_ts = time.time()
        self.vol_dn = vol_dn
        self.vol_up = vol_up
        GPIO.setup(self.vol_dn, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.vol_up, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.down = self.up = False

    def update(self, ts):
        self.down = GPIO.input(self.vol_dn)
        self.up = GPIO.input(self.vol_up)


def update_volume(buttons, vol):
    new_vol = vol

    if buttons.up:
        new_vol += 5
    if buttons.down:
        new_vol -= 5

    new_vol = min(max(new_vol, MIN_VOL), MAX_VOL)
    return (new_vol, vol != new_vol)


def main_loop():
    vis = Vis()
    buttons = Buttons(20, 21)
    while True:
        ts = time.time()

        # Don't care about stereo, we'll even levels on first volume
        # change anyway.
        mixer = alsaaudio.Mixer('Speaker')
        vol = max(mixer.getvolume())

        buttons.update(ts)
        (vol, changed) = update_volume(buttons, vol)
        if changed:
            mixer.setvolume(vol, alsaaudio.MIXER_CHANNEL_ALL)

        vis.set_volume(vol)
        vis.update_display(ts)
        time.sleep(0.1)

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    main_loop()
