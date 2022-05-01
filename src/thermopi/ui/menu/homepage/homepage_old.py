# A demo of LCD/TFT SCREEN DISPLAY with touch screen
# A "penprint" is made to screen wherever the pen is touched to screen
#
# import matplotlib.path as mpltPath
import datetime

import RPi.GPIO as GPIO
import os
import spidev
from time import sleep, time

from PIL import ImageFont, ImageDraw
from PIL import Image

# from lib_tft24T import TFT24T
# from libs.ili9341.tft import TFTDisplay
from thermopi.libs.ili9341.tft import TFTDisplay
from thermopi.ui.helpers import draw_text

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# temperature
DEGREE_SIGN = chr(176)
CELSIUS_SIGN = "{}{}".format(DEGREE_SIGN, "C")
FAHRENHEIT_SIGN = "{}{}".format(DEGREE_SIGN, "F")

# ui
IMG_PATH = "{}/../../../images/".format(os.path.dirname(__file__))
# BACKGROUND_COLOR = (59, 110, 165)  # windows blue
BACKGROUND_COLOR = (2, 53, 98)  # windows blue

# fonts
MAIN_FONT_PATH = "{}/../../../fonts/asimov/Asimov.otf".format(os.path.dirname(__file__))
DEFAULT_FONT = ImageFont.truetype(MAIN_FONT_PATH, 26)
FONT_18 = ImageFont.truetype(MAIN_FONT_PATH, 18)
FONT_12 = ImageFont.truetype(MAIN_FONT_PATH, 12)

# pin-outs
DC = 24
RST = 25
LED = 5
PEN = 26

TFT = TFTDisplay(spidev.SpiDev(), GPIO, landscape=False)

# Initialize display.
TFT.init_lcd(DC, RST, LED)
TFT.init_touch_screen(PEN)

draw = TFT.draw()
TFT.clear(BACKGROUND_COLOR)

TFT.display()

polygon_down = (160, 200), (160, 235), (180, 235), (180, 200)
# path_down = mpltPath.Path(polygon_down, closed=True)

polygon_up = (110, 210), (105, 235), (135, 235), (140, 205)
# path_up = mpltPath.Path(polygon_up, closed=True)


decimal_pttrn = '{:.2f}'

MENU_IMG_PATH = os.path.join(IMG_PATH, "menu.png")
TEMP_UP_DOWN_IMG_PATH = os.path.join(IMG_PATH, "arrow.png")
POWER_ON_IMG_PATH = os.path.join(IMG_PATH, "blue_power_button.png")
POWER_OFF_IMG_PATH = os.path.join(IMG_PATH, "red_power_button.png")
TEMP_UP_DOWN_IMG = Image.open(TEMP_UP_DOWN_IMG_PATH)
POWER_ON_IMG = Image.open(POWER_ON_IMG_PATH)
POWER_OFF_IMG = Image.open(POWER_OFF_IMG_PATH)
MENU_IMAGE = Image.open(MENU_IMG_PATH)

start_time = time()


def draw_temp_down_bttn():
    # draw.line((10, 260, 60, 260), fill="black")
    # draw.line((60, 310, 60, 260), fill="brown")
    # draw.line((10, 310, 60, 310), fill="red")
    # draw.line((10, 260, 10, 310), fill="purple")
    img_down = TEMP_UP_DOWN_IMG.rotate(270, 0).resize((50, 50))
    draw.paste_image(img_down, (10, 260), add_mask=True)  # custom method for coloured image


def draw_temp_up_bttn():
    # draw.line((80, 260, 130, 260), fill="black")
    # draw.line((130, 310, 130, 260), fill="brown")
    # draw.line((80, 310, 130, 310), fill="red")
    # draw.line((80, 260, 80, 310), fill="purple")
    img_up = TEMP_UP_DOWN_IMG.rotate(90, 0).resize((50, 50))
    draw.paste_image(img_up, (80, 260), add_mask=True)  # custom method for coloured image


def draw_power_bttn():
    # draw.line((80, 260, 130, 260), fill="black")
    # draw.line((130, 310, 130, 260), fill="brown")
    # draw.line((80, 310, 130, 310), fill="red")
    # draw.line((80, 260, 80, 310), fill="purple")
    img_power = POWER_ON_IMG.rotate(270, 0).resize((80, 80))
    draw.paste_image(img_power, (130, 240), add_mask=True)  # custom method for coloured image


def draw_main_temperature(main_temp=None):
    if not main_temp:
        main_temp = 23.50
    draw_text(draw=draw, text=decimal_pttrn.format(main_temp), position=(110, 110),
              font=DEFAULT_FONT, color="brown", bg_color=BACKGROUND_COLOR)
    draw_text(draw, "{}".format(CELSIUS_SIGN), (110, 180), DEFAULT_FONT, "white", bg_color=BACKGROUND_COLOR)


def draw_min_max_temp():
    draw.line((100, 150, 80, 150), fill="white")
    draw_text(draw, "{}{}".format(22, DEGREE_SIGN), (85, 115), FONT_18, "white", bg_color=BACKGROUND_COLOR)
    draw_text(draw, "{}{}".format(23, DEGREE_SIGN), (85, 160), FONT_18, "white", bg_color=BACKGROUND_COLOR)


def draw_date_and_time():
    dt_now = datetime.datetime.now()
    time_now = dt_now.strftime('%a, %d %b %Y %H:%M:%S')
    draw_text(draw, "{:25}".format(time_now), (10, 10), FONT_12, "white", bg_color=BACKGROUND_COLOR)


def draw_menu():
    menu_image = MENU_IMAGE.rotate(270).resize((40, 40))
    draw.paste_image(menu_image, (190, 10), add_mask=True)  # custom method for coloured image


def draw_satellite_temperatures():
    draw.line((225, 270, 205, 270), fill="black")
    draw.line((225, 220, 205, 220), fill="black")
    draw.line((225, 170, 205, 170), fill="black")
    draw_text(draw, "{}{}".format(21, DEGREE_SIGN), (210, 280), FONT_18, "black", bg_color=BACKGROUND_COLOR)
    draw_text(draw, "{}{}".format(22, DEGREE_SIGN), (210, 230), FONT_18, "black", bg_color=BACKGROUND_COLOR)
    draw_text(draw, "{}{}".format(23, DEGREE_SIGN), (210, 180), FONT_18, "black", bg_color=BACKGROUND_COLOR)
    draw_text(draw, "{}{}".format(24, DEGREE_SIGN), (210, 130), FONT_18, "black", bg_color=BACKGROUND_COLOR)


def init():
    draw_power_bttn()
    draw_temp_down_bttn()
    draw_temp_up_bttn()
    draw_main_temperature()
    draw_min_max_temp()
    draw_date_and_time()
    draw_menu()
    draw_satellite_temperatures()

    TFT.display()


def modify_temp(main_temperature):
    global start_time
    # print('main_temperature is:', main_temperature)
    if TFT.pen_down():
        start_time = time()
        if TFT.light_status:
            TFT.back_light(False)
        pen_position = TFT.pen_position()
        print("position is:", pen_position)
        if TFT.pen_on_hotspot(polygon_down, pen_position):
            print('arrow down', pen_position)
            main_temperature -= 0.25
        elif TFT.pen_on_hotspot(polygon_up, pen_position):
            print('arrow up', pen_position)
            main_temperature += 0.25
    draw_main_temperature(main_temperature)
    draw_date_and_time()

    TFT.display()

# init()
# while 1:
#    modify_temp(20)
#    if time() - start_time > 30 and not TFT.light_status:
#        TFT.back_light(True)
