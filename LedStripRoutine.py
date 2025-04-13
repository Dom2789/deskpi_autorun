import threading
import time
from rpi_ws281x import PixelStrip, Color
import argparse

class Strip_Routine(threading.Thread):
    def __init__(self):
        super(Strip_Routine, self).__init__()
        # LED strip configuration:
        LED_COUNT = 120        # Number of LED pixels.
        LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
        # LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
        LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
        LED_DMA = 10          # DMA channel to use for generating signal (try 10)
        LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
        LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
        LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
        # Create NeoPixel object with appropriate configuration.
        self.strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        # Intialize the library (must be called once before other functions).
        self.strip.begin()
    
    
    def run(self):
        i = 0
        self.colorWipe(self.strip, Color(0, 0, 0), 10)
        while True:
            print(i)
            self.rainbowCycle(self.strip)
            i += 1


    def rainbowCycle(self, strip, wait_ms=20, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256 * iterations):
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, self.wheel(
                    (int(i * 256 / strip.numPixels()) + j) & 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)    


    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)


    def colorWipe(self, strip, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)        
