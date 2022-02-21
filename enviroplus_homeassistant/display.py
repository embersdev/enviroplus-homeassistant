import os
import time
import numpy
import ST7735
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from fonts.ttf import RobotoMedium as UserFont
import logging

class EnviroPlusDisplay:

    # Create LCD class instance.
    disp = ST7735.ST7735(
        port=0,
        cs=1,
        dc=9,
        backlight=12,
        rotation=270,
        spi_speed_hz=4000000
    )

    # Width and height to calculate text position.
    WIDTH = disp.width
    HEIGHT = disp.height

     # Base Path
    path = os.path.dirname(os.path.realpath(__file__))

    # Fonts
    font_sm = ImageFont.truetype(UserFont, 12)
    font_lg = ImageFont.truetype(UserFont, 30)

    # Text settings.
    font_size = 25
    font = ImageFont.truetype(UserFont, font_size)
    text_colour = (215, 215, 0)  # gold
    #text_colour = (20, 100, 140) # blue
    back_colour = (0, 0, 0)

    # Margins
    margin = 1

    CURRENT_TEMPERATURE = 0
    CURRENT_HUMIDITY = 0

    temp_icon = Image.open(f"{path}/icons/temperature.png")
    humidity_icon = Image.open(f"{path}/icons/humidity.png")
    trooper = Image.open(f"{path}/images/trooper80.png")

    def __init__(self, enabled:bool = True):
        #logging.info(f"{self.HEIGHT}x{self.WIDTH}")
        self.enabled = enabled
        # Initialize display.
        self.disp.begin()
            # New canvas to draw on.
        img = Image.new('RGBA', (self.WIDTH, self.HEIGHT), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        logging.info("Display Enabled: %s", self.enabled)

    def overlay_text(self, img, position, text, font, align_right=False, rectangle=False):
        #text_colour = (215, 215, 0)  # gold
        #img = Image.new('RGBA', (self.WIDTH, self.HEIGHT), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        w, h = font.getsize(text)
        x, y = position
        if align_right:
            x, y = position
            x -= w
            position = (x, y)
        if rectangle:
            x += 1
            y += 1
            position = (x, y)
            border = 1
            rect = (x - border, y, x + w, y + h + border)
            rect_img = Image.new('RGBA', (self.WIDTH, self.HEIGHT), color=(0, 0, 0, 0))
            rect_draw = ImageDraw.Draw(rect_img)
            rect_draw.rectangle(rect, (255, 255, 255))
            rect_draw.text(position, text, font=font, fill=(0, 0, 0, 0))
            img = Image.alpha_composite(img, rect_img)
        else:
            draw.text(position, text, font=font, fill=self.text_colour)
        return img

    def refresh(self, sensor_name, value):
        img = Image.new('RGBA', (self.WIDTH, self.HEIGHT), color=(0, 0, 0))

        #logging.info(f"{sensor_name} = {value}")

        if(sensor_name == "temperature"):
            self.CURRENT_TEMPERATURE = value
        if(sensor_name == "humidity"):
            self.CURRENT_HUMIDITY = value

        fahrenheit = (self.CURRENT_TEMPERATURE * 1.8) + 32
        temp_string = f"{fahrenheit:.0f}°F"
        img = self.overlay_text(img, (27, 4), temp_string, self.font_lg)
        img.paste(self.temp_icon, (self.margin, 8), mask=self.temp_icon)

        # Humidity
        humidity_string = f"{self.CURRENT_HUMIDITY:.0f}%"
        img = self.overlay_text(img, (27, 42), humidity_string, self.font_lg)
        img.paste(self.humidity_icon, (self.margin, 47), mask=self.humidity_icon)

        # Trooper
        img.paste(self.trooper, (84, 0), mask=self.trooper)

        self.disp.display(img)

    def off(self):
        self.disp.set_backlight(0)
