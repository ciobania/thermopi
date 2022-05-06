#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# author: 'ACIOBANI'
from enum import Enum

from PIL import ImageChops, ImageDraw, ImageFont
from PIL import Image


def _draw_text(text, font, text_color, bg_color="black", rotate_degree=270):
    text_size = tuple(reversed(font.getsize(text)))
    # img = Image.new("RGB", (100, 100), color=bg_color)
    # idd_text_size = ImageDraw.Draw(img).textlength(text)

    im = Image.new("RGB", text_size, color=bg_color)
    # im = im.rotate(90, resample=Image.BICUBIC, expand=True)
    alpha = Image.new("L", im.size, 0)
    # alpha = alpha.rotate(90, resample=Image.BICUBIC, expand=True)
    # Make a grayscale image of the font, white on black.
    im_text = Image.new("L", im.size, 0)
    # im_text = im_text.rotate(90, resample=Image.BICUBIC, expand=True)
    # dr_text = ImageDraw.Draw(im_text)
    # dr_text.text((5, 5), text, font=default_font, fill="white")

    # Add the white text to our collected alpha channel. Gray pixels around
    # the edge of the text will eventually become partially transparent
    # pixels in the alpha channel.
    alpha = ImageChops.lighter(alpha, im_text)
    # alpha.resize(im_text.size)
    # alpha = alpha.rotate(90, resample=Image.BICUBIC, expand=True)

    # Make a solid color, and add it to the color layer on every pixel
    # that has even a little of alpha showing.
    solid_color = Image.new("RGBA", im.size, text_color)

    im_mask = Image.eval(im_text, lambda p: 255 * (int(p != 0)))
    # im_mask = im_mask.resize(solid_color.size)
    # im_mask = im_mask.rotate(90, resample=Image.BICUBIC, expand=True)

    # print(im.mode, alpha.mode, solid_color.mode)
    im = Image.composite(solid_color, im, im_mask)
    # im = im.rotate(90, resample=Image.BICUBIC, expand=True)
    im.putalpha(alpha)

    return im


def draw_text(draw, text, position, font, color, bg_color="black", landscape=True):
    if landscape:
        rotate_degree = 270
    else:
        rotate_degree = 0
    im = _draw_text(str(text), font, text_color=color, bg_color=bg_color, rotate_degree=rotate_degree)
    draw.paste_image(im, position)
    draw.text_rotated(position, str(text), rotate_degree, font=font, fill=color)


class ExtendedEnum(Enum):
    def __get__(self, instance, owner):
        return self.value


class DisplayBgrColor(ExtendedEnum):
    RED = (135, 62, 35)
    GREEN = (0, 255, 0)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    WIN_BLUE = (59, 119, 188)
