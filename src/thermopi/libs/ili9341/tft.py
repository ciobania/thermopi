# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# author: 'ACIOBANI'

# This is Python 3 version of the ILI9341 tft24T V0.3 from April 2015
# written by Brian Lavery forTJCTM24024-SPI 2.4 inch Touch 320x240 SPI LCD
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so.

import numbers
import textwrap
import time
from types import MethodType

from PIL import Image
from PIL import ImageDraw

# Calibration scaling values from the calibration utility:
# Makes touchscreen coordinates agree with TFT coordinates (240x320) for YOUR device
# You may need to adjust these values for YOUR device
from thermopi.libs.ili9341.geometry import is_inside_polygon

calib_scale240 = 240
calib_scale320 = -320
calib_offset240 = 10
calib_offset320 = -310

margin = 13
# "margin" is a no-go perimeter (in pixels).  [Stylus at very edge of touchscreen is rather jitter-prone.]
# GPIO.setwarnings(False)

# Constants for interacting with display registers.
ILI9341_TFTWIDTH = 240
ILI9341_TFTHEIGHT = 320

ILI9341_SWRESET = 0x01
ILI9341_SLPOUT = 0x11
ILI9341_INVOFF = 0x20
ILI9341_INVON = 0x21
ILI9341_GAMMASET = 0x26
ILI9341_DISPON = 0x29
ILI9341_CASET = 0x2A
ILI9341_PASET = 0x2B
ILI9341_RAMWR = 0x2C
ILI9341_RAMRD = 0x2E
ILI9341_MADCTL = 0x36
ILI9341_PIXFMT = 0x3A
ILI9341_FRMCTR1 = 0xB1
ILI9341_DFUNCTR = 0xB6

ILI9341_PWCTR1 = 0xC0
ILI9341_PWCTR2 = 0xC1
ILI9341_VMCTR1 = 0xC5
ILI9341_VMCTR2 = 0xC7
ILI9341_GMCTRP1 = 0xE0
ILI9341_GMCTRN1 = 0xE1


# Buffer = Image


class TFTDisplay:
    X = 0xD0
    Y = 0x90
    Z1 = 0xB0
    Z2 = 0xC0

    def __init__(self, spi, gpio, landscape=False):
        self.light_status = None
        self._led = None
        self._rst = None
        self._ce_lcd = None
        self._spi_speed_lcd = None
        gpio.setwarnings(False)
        self.buffer2 = None
        self._dc = None
        self._pen = None
        self._spi_speed_tch = None
        self._ce_tch = None
        self.is_landscape = landscape
        self._spi = spi
        self._gpio = gpio
        self.buffer = Image.Image()

    def init_touch_screen(self, pen, ce=1, spi_speed=10000000):
        self._ce_tch = ce
        self._spi_speed_tch = spi_speed
        self._pen = pen
        self._gpio.setup(pen, self._gpio.IN)

    def pen_down(self):
        # reads True when stylus is in contact
        return not self._gpio.input(self._pen)

    def read_value(self, channel):
        #        self._spi.open(0, self._ce_tch)
        self._spi.open(1, self._ce_tch)
        self._spi.max_speed_hz = self._spi_speed_tch

        response_data = self._spi.xfer([channel, 0, 0])
        self._spi.close()
        return (response_data[1] << 5) | (response_data[2] >> 3)
        # Pick off the 12-bit reply

    def pen_position(self):
        self.read_value(self.X)
        self.read_value(self.Y)
        self.read_value(self.X)
        self.read_value(self.Y)
        # burn those
        x = 0
        y = 0
        for k in range(10):
            x += self.read_value(self.X)
            y += self.read_value(self.Y)
        # average those
        x /= 10
        y /= 10
        # empirically set calibration factors:
        x2 = (4096 - x) * calib_scale240 / 4096 - calib_offset240
        y2 = y * calib_scale320 / 4096 - calib_offset320
        # So far, these co-ordinates are the native portrait mode

        if y2 < margin or y2 > (319 - margin) or x2 < margin or x2 > (239 - margin):
            x2 = 0
            y2 = 0
        # The fringes of touchscreen give a lot of erratic/spurious results
        # Don't allow fringes to return anything.
        # (Also, user should not program hotspots/icons out in the margin,
        # to discourage pointing pen there)
        # a return of (0,0) is considered a nul return

        if self.is_landscape:
            # rotate the coordinates
            x2, y2 = y2, x2
            # x3 = x2
            # x2 = 319 - y2
            # y2 = x3
        return [x2, y2]

    def send2lcd(self, data, is_data=True, chunk_size=4096):
        """
        Send data to LCD.
        """
        # Set DC low for command, high for data.
        self._gpio.output(self._dc, is_data)
        self._spi.close()  # close any channels already open?
        self._spi.open(0, self._ce_lcd)
        self._spi.max_speed_hz = self._spi_speed_lcd

        # Convert scalar argument to list so either can be passed as parameter.
        if isinstance(data, (numbers.Number, int)):
            data = [data & 0xFF]

        # Write data a chunk at a time.
        for start in range(0, len(data), chunk_size):
            end = min(start + chunk_size, len(data))
            self._spi.writebytes(data[start:end])
        self._spi.close()

    def command(self, data):
        """
        Write a byte or array of bytes to the display as command data.
        """
        self.send2lcd(data, False)

    def data(self, data):
        """
        Write a byte or array of bytes to the display as display data.
        """
        self.send2lcd(data, True)

    def reset_lcd(self):
        if self._rst is not None:
            self._gpio.output(self._rst, self._gpio.HIGH)
            time.sleep(0.005)
            self._gpio.output(self._rst, self._gpio.LOW)
            time.sleep(0.02)
            self._gpio.output(self._rst, self._gpio.HIGH)
            time.sleep(0.150)
        else:
            self.command(ILI9341_SWRESET)
            time.sleep(1)

    # dict(
    # ILI9341_SWRESET = (0x01, None),
    # ILI9341_SLPOUT = (0x11, None),
    # ILI9341_INVOFF = (0x20, None),
    # ILI9341_INVON = (0x21, None),
    # ILI9341_GAMMASET = (0x26, 0x01),
    # ILI9341_DISPON = (0x29, None),
    # ILI9341_CASET = (0x2A, None),
    # ILI9341_PASET = (0x2B, None),
    # ILI9341_RAMWR = (0x2C, None),
    # ILI9341_RAMRD = (0x2E, None),
    # ILI9341_MADCTL = (0x36, [0x48, 0x40, 0x80, 0x20, 0x08]),
    # ILI9341_PIXFMT = (0x3A, 0x55),
    # ILI9341_FRMCTR1 = (0xB1, [0x00, 0x18]),
    # ILI9341_DFUNCTR = (0xB6, [0x08, 0x82, 0x27]),
    # ILI9341_PWCTR1 = (0xC0, 0x23),
    # ILI9341_PWCTR2 = (0xC1, 0x10),
    # ILI9341_VMCTR1 = (0xC5, [0x3e, 0x28]),
    # ILI9341_VMCTR2 = (0xC7, 0x86),
    # ILI9341_3GMDSB = (0xF2, 0x00),
    # ILI9341_GMCTRP1 = (0xE0, [0x0F, 0x31, 0x2b, 0x0c, 0x0e, 0x08, 0x4e, 0xf1, 0x37, 0x07, 0x10, 0x03, 0x0e, 0x09, 0x00]),
    # ILI9341_GMCTRN1 = (0xE1, [0x00, 0x0e, 0x14, 0x03, 0x11, 0x07, 0x31, 0xc1, 0x48, 0x08, 0x0f, 0x0c, 0x31, 0x36, 0x0f]))
    def _init9341(self):
        lcd_init_data = {
            'ILI9341_SWRESET': (1, None),
            'ILI9341_SLPOUT': (17, None),
            'ILI9341_INVOFF': (32, None),
            'ILI9341_INVON': (33, None),
            'ILI9341_GAMMASET': (38, 1),
            'ILI9341_DISPON': (41, None),
            'ILI9341_CASET': (42, None),
            'ILI9341_PASET': (43, None),
            'ILI9341_RAMWR': (44, None),
            'ILI9341_RAMRD': (46, None),
            'ILI9341_MADCTL': (54, [72, 64, 128, 32, 8]),
            'ILI9341_PIXFMT': (58, 85),
            'ILI9341_FRMCTR1': (177, [0, 24]),
            'ILI9341_DFUNCTR': (182, [8, 130, 39]),
            'ILI9341_PWCTR1': (192, 35),
            'ILI9341_PWCTR2': (193, 16),
            'ILI9341_VMCTR1': (197, [62, 40]),
            'ILI9341_VMCTR2': (199, 134),
            'ILI9341_3GMDSB': (242, 0),
            'ILI9341_GMCTRP1': (224,
                                [15, 49, 43, 12, 14, 8, 78, 241, 55, 7, 16, 3, 14, 9, 0]),
            'ILI9341_GMCTRN1': (225,
                                [0, 14, 20, 3, 17, 7, 49, 193, 72, 8, 15, 12, 49, 54, 15])}
        for cmd_name, (cmd_address, cmd_value) in list(lcd_init_data.items()):
            if cmd_name in ('ILI9341_SWRESET', 'ILI9341_INVOFF', 'ILI9341_INVON',
                            'ILI9341_CASET', 'ILI9341_PASET', 'ILI9341_RAMWR', 'ILI9341_RAMRD'):
                continue
            elif cmd_name == 'ILI9341_SLPOUT':
                self.command(cmd_address)
                time.sleep(0.120)
            elif cmd_name == 'ILI9341_DISPON':
                self.command(cmd_address)
            else:
                self.command(cmd_address)
                if cmd_value:
                    self.data(cmd_value)

    def init_lcd(self, dc=None, rst=None, led=None, ce=0, spi_speed=10000000):
        self._dc = dc
        self._rst = rst
        self._led = led
        self._ce_lcd = ce
        self._spi_speed_lcd = spi_speed
        # Set DC as output.
        self._gpio.setup(dc, self._gpio.OUT)
        # Setup reset as output (if provided).
        if rst is not None:
            self._gpio.setup(rst, self._gpio.OUT)
        if led is not None:
            self._gpio.setup(led, self._gpio.OUT)
            self._gpio.output(led, self._gpio.HIGH)

        # Create an image buffer.
        if self.is_landscape:
            self.buffer = Image.new('RGB', (ILI9341_TFTHEIGHT, ILI9341_TFTWIDTH))
        else:
            self.buffer = Image.new('RGB', (ILI9341_TFTWIDTH, ILI9341_TFTHEIGHT))
        # and a backup buffer for backup/restore
        self.buffer2 = self.buffer.copy()
        self.reset_lcd()
        self._init9341()

    def set_frame(self, x0=0, y0=0, x1=None, y1=None):
        x0 = int(x0)
        y0 = int(y0)
        if x1 is None:
            x1 = int(ILI9341_TFTWIDTH - 1)
        else:
            x1 = int(x1)
        if y1 is None:
            y1 = int(ILI9341_TFTHEIGHT - 1)
        else:
            y1 = int(y1)
        self.command(ILI9341_CASET)  # Column addr
        self.data([x0 >> 8, x0, x1 >> 8, x1])
        self.command(ILI9341_PASET)  # Row addr
        self.data([y0 >> 8, y0, y1 >> 8, y1])
        self.command(ILI9341_RAMWR)

    def display(self, image=None):
        """Write the display buffer or provided image to the hardware.  If no
        image parameter is provided the display buffer will be written to the
        hardware.  If an image is provided, it should be RGB format and the
        same dimensions as the display hardware.
        """
        # By default, write the internal buffer to the display.
        if image is None:
            image = self.buffer
        if image.size[0] == 320:
            image = image.rotate(90)

        # Set address bounds to entire display.
        self.set_frame()
        # Convert image to array of 16bit 565 RGB data bytes.
        pixel_bytes = list(self.image_to_data(image))
        # Write data to hardware.
        self.data(pixel_bytes)

    def pen_print(self, position, size):
        """
        Print PEN point, at given position
        """
        x, y = position
        if self.is_landscape:
            # rotate the coordinates. The intrinsic hardware is portrait
            x3 = x
            x = y
            y = 319 - x3
        self.set_frame(x, y - size, x + size, y + size)
        pixel_bytes = [0] * (size * size * 8)
        self.data(pixel_bytes)

    def clear(self, color=(0, 0, 0)):
        """
        Clear the image buffer to the specified RGB color (default black).
        USE (r, g, b) NOTATION FOR THE COLOUR !!
        """

        if not isinstance(color, (tuple, list)):
            print("clear() function colours must be in (255,255,0) form")
            exit()
        width, height = self.buffer.size
        self.buffer.putdata([color] * (width * height))
        self.display()

    def draw(self):
        """
        Return a PIL ImageDraw instance for drawing on the image buffer.
        """
        # image2 = Image.new('RGBA', (320, 240), (0, 0, 0, 0))

        d = ImageDraw.Draw(self.buffer)
        d.buffer = self.buffer
        # Add custom methods to the draw object:
        d.text_rotated = MethodType(_text_rotated, d)
        d.paste_image = MethodType(_paste_image, d)
        d.text_wrapped = MethodType(_text_wrapped, d)
        return d

    def load_wallpaper(self, filename):
        # The image should be 320x240 or 240x320 only (full wallpaper!). Errors otherwise.
        # We need to cope with whatever orientations file image and TFT canvas are.
        image = Image.open(filename)
        if image.size[0] > self.buffer.size[0]:
            self.buffer.paste(image.rotate(90))
        elif image.size[0] < self.buffer.size[0]:
            self.buffer.paste(image.rotate(-90))
        else:
            self.buffer.paste(image)

    def backup_buffer(self):
        self.buffer2.paste(self.buffer)

    def restore_buffer(self):
        self.buffer.paste(self.buffer2)

    def invert(self, onoff):
        if onoff:
            self.command(ILI9341_INVON)
        else:
            self.command(ILI9341_INVOFF)

    def back_light(self, off):
        if self._led is not None:
            self._gpio.output(self._led, self._gpio.LOW if off else self._gpio.HIGH)
            self.light_status = off

    @staticmethod
    def image_to_data(image):
        """Generator function to convert a PIL image to 16-bit 565 RGB bytes."""
        # Source of this code: Adafruit ILI9341 python project
        pixels = image.convert('RGB').load()
        width, height = image.size
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[(x, y)]
                color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                yield (color >> 8) & 0xFF
                yield color & 0xFF

    def text_direct(self, pos, text, font, fill="white"):

        width, height = self.draw().textsize(text, font=font)
        # Create a new image with transparent background to store the text.
        textimage = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        # Render the text.
        text_draw = ImageDraw.Draw(textimage)
        text_draw.text((0, 0), text, font=font, fill=fill)
        self.set_frame(pos[0], pos[1], pos[0] + width - 1, pos[1] + height - 1)
        # Convert image to array of 16bit 565 RGB data bytes.
        pixel_bytes = list(self.image_to_data(textimage))
        # Write data to hardware.
        self.data(pixel_bytes)

    @staticmethod
    def pen_on_hotspot(hs_list, position):
        if is_inside_polygon(hs_list, position):
            return True

        return False


# CUSTOM FUNCTIONS FOR draw() IN LCD CANVAS SYSTEM

# We import these extra functions below as new custom methods of the PIL "draw" function:
# Hints on this custom method technique:
#     http://www.ianlewis.org/en/dynamically-adding-method-classes-or-class-instanc

def _text_rotated(self, position, text, angle, font, fill="white"):
    # Define a function to create rotated text.
    # Source of this rotation coding: Adafruit ILI9341 python project
    # "Unfortunately PIL doesn't have good
    # native support for rotated fonts, but this function can be used to make a
    # text image and rotate it, so it's easy to paste in the buffer."
    width, height = self.textsize(text, font=font)
    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    # Render the text.
    text_draw = ImageDraw.Draw(textimage)
    text_draw.text((0, 0), text, font=font, fill=fill, stroke_fill=fill)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=True)
    # Paste the text into the TFT canvas image, using text itself as a mask for transparency.
    self.buffer.paste(rotated, position, rotated)  # into the global Buffer
    #   example:  draw.text_rotated(position, text, angle, font, fill)


def _paste_image(self, filename, position, add_mask=False):
    if isinstance(filename, str):
        self.buffer.paste(Image.open(filename), position)
    else:
        if add_mask:
            self.buffer.paste(filename, position, mask=filename)
        else:
            self.buffer.paste(filename, position)


def _text_wrapped(self, position, text1, length, height, font, fill="white"):
    text2 = textwrap.wrap(text1, length)
    y = position[1]
    for t in text2:
        self.text((position[0], y), t, font=font, fill=fill)
        y += height
