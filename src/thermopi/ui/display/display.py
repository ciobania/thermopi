#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# author: 'ACIOBANI'

import os
import pygame
import pygame_widgets
import sys

from time import time

from thermopi import FONTS_DIR
from thermopi.ui.core.Screen import Screen

from thermopi.ui.menu.scheduler.scheduler import scheduler

from thermopi.ui.menu.settings.settings import settings

from thermopi.ui.menu.homepage.homepage import homepage

try:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(5, GPIO.OUT)
except ModuleNotFoundError as _:
    GPIO = None

os.environ["SDL_FBDEV"] = "/dev/fb1"


LED_PIN = 5
PEN_PIN = 26
WIDTH = 320
HEIGHT = 240
SCREEN_RECT = pygame.Rect(0, 0, WIDTH, HEIGHT)

if pygame.get_sdl_version()[0] == 2:
    pygame.mixer.pre_init(44100, 32, 2, 1024)
pygame.init()
if pygame.mixer and not pygame.mixer.get_init():
    print("Warning, no sound")
    pygame.mixer = None

# Set the display mode
best_depth = pygame.display.mode_ok(SCREEN_RECT.size, pygame.NOFRAME, 32)
screen = pygame.display.set_mode(SCREEN_RECT.size, pygame.NOFRAME, best_depth)


pygame.display.set_caption("ThermoPi")
pygame.mouse.set_visible(False)
pygame.event.set_allowed([pygame.MOUSEBUTTONDOWN, pygame.QUIT])

font_path = os.path.join(FONTS_DIR, 'FreeSerifItalic.ttf')

START_TIME = time()
GET_TEMP_TIME = time()
RUN_HEAT_TIME = time()
# THERMOSTAT = Thermostat()


def check_display_light_status(pen_status=False):
    global START_TIME
    if GPIO:
        now_time = time()
        display_status = GPIO.input(LED_PIN)
        if now_time - START_TIME > 30 and display_status:
            GPIO.output(LED_PIN, GPIO.LOW)
            # LOG.info("PEN_UP: start_time, now_time: {} {} {}".format(START_TIME, now_time, display_status))

        if pen_status:
            START_TIME = time()
            if not display_status:
                GPIO.output(LED_PIN, GPIO.HIGH)
            # LOG.info("PEN_DOWN: start_time, now_time: {} {} {}".format(start_time, now_time, TFT.light_status))


# main loop
m = Screen(screen, '', width=WIDTH, height=HEIGHT)
win = m.make_current()

run_display = True
while run_display:
    pen_status = False
    win.screen_update()
    events = pygame.event.get()

    if win.drop_down.getSelected() in (1, None):
        homepage(win, events)
    elif win.drop_down.getSelected() == 2:
        scheduler(win)
    elif win.drop_down.getSelected() == 3:
        settings(win)
    elif win.drop_down.getSelected() == 'restart':
        print(f'Restarting with sys.argv:: {sys.argv}')
        os.execv(sys.executable, ['python3'] + sys.argv)

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_presses = pygame.mouse.get_pressed()
            if mouse_presses[0]:
                pen_status = True

    pygame_widgets.update(events)
    pygame.display.update()
    check_display_light_status(pen_status=pen_status)

pygame.quit()
sys.exit()
