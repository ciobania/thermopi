#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# author: 'ACIOBANI'

import datetime
import os
import pygame

from time import time

from thermopi import FONTS_DIR, IMAGES_DIR, LOGGER
from thermopi.libs.thermostat.thermostat import Thermostat

try:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(5, GPIO.OUT)
except ModuleNotFoundError as _:
    GPIO = None

font_path = os.path.join(FONTS_DIR, 'FreeSerifItalic.ttf')

START_TIME = time()
GET_TEMP_TIME = time()
RUN_HEAT_TIME = time()
THERMOSTAT = Thermostat()


def draw_up_temp_button(win, x, y):
    return _draw_arrow_button(win, x, y, 180)


def draw_down_temp_button(win, x, y):
    return _draw_arrow_button(win, x, y, 0)


def _draw_arrow_button(win, x, y, angle):
    _arrow_png_path = os.path.join(IMAGES_DIR, 'arrow.png')
    _arrow = pygame.image.load(_arrow_png_path)
    _arrow = pygame.transform.scale(_arrow, (40, 40))
    _arrow = pygame.transform.rotate(_arrow, angle)
    return win.screen.blit(_arrow, (x, y))  # x, y coordinates


def draw_button(win, text, x, y):
    # light shade of the button
    color_light = (170, 170, 170)
    # dark shade of the button
    color_dark = (100, 100, 100)
    button_font = pygame.font.SysFont(font_path,
                                      20,
                                      bold=False)
    text = button_font.render(text, True, color_light)
    rect = pygame.draw.rect(win.screen, color_dark, [x, y, 80, 40])
    win.screen.blit(text, (int(rect.center[0] - text.get_size()[0] / 2),
                           int(rect.center[1] - text.get_size()[1] / 2)))


def get_thermostat_data(temp_data):
    relay_state = ""
    tolerance = THERMOSTAT.schedule['all_week']['interval'][0]['general_temp']['tolerance']
    min_temp = THERMOSTAT.schedule['all_week']['interval'][0]['general_temp']['min']
    max_temp = THERMOSTAT.schedule['all_week']['interval'][0]['general_temp']['max']
    if temp_data['temperature'] < min_temp or temp_data['temperature'] < min_temp + tolerance:
        if not THERMOSTAT.get_relay_state(THERMOSTAT.cfg['relay_channel']):
            THERMOSTAT.relay_on(THERMOSTAT.cfg['relay_channel'])
            relay_state = "ON"
    elif min_temp < temp_data['temperature'] <= max_temp or temp_data['temperature'] > max_temp:
        if THERMOSTAT.get_relay_state(THERMOSTAT.cfg['relay_channel']):
            THERMOSTAT.relay_off(THERMOSTAT.cfg['relay_channel'])
            relay_state = "OFF"

    LOGGER.info(THERMOSTAT.status_msg.format(relay_state,
                                             datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                                             temp_data['temperature'],
                                             temp_data['humidity']))


new_temp = THERMOSTAT.schedule['all_week']['interval'][0]['general_temp']['min']
min_temp = THERMOSTAT.schedule['all_week']['interval'][0]['general_temp']['min']
max_temp = THERMOSTAT.schedule['all_week']['interval'][0]['general_temp']['max']


def homepage(win, events):
    global GET_TEMP_TIME, RUN_HEAT_TIME, new_temp
    temperature_data = None

    # TODO: move following 120 seconds delay into scheduler config
    if time() - GET_TEMP_TIME > 120 or not temperature_data:
        GET_TEMP_TIME = time()
        temperature_data = THERMOSTAT.get_thermostat_data()
    if time() - RUN_HEAT_TIME > 900 or not temperature_data:
        get_thermostat_data(temperature_data)
        RUN_HEAT_TIME = time()

    # Draw side buttons and temp
    up_temp = draw_up_temp_button(win, 280, int(win.height / 2) - 60)
    win.draw_text(f'{new_temp}°', win.colors.BLACK, 300, int(win.height / 2), 20)
    down_temp = draw_down_temp_button(win, 280, int(win.height / 2) + 20)

    # Draw satellites temperature
    win.draw_text('L: 21°', win.colors.BLACK, 20, 100, 20)  # TODO: this will come from BLE satellites
    win.draw_text('M: 22°', win.colors.BLACK, 20, 130, 20)  # TODO: this will come from BLE satellites
    win.draw_text('S: 23°', win.colors.BLACK, 20, 160, 20)  # TODO: this will come from BLE satellites

    # Draw main, min and max temp
    win.draw_text(f"{int(temperature_data['temperature'])}°",
                  win.colors.WHITE,
                  int(win.width / 2),
                  int(win.height / 2),
                  60)
    win.draw_text(f"{min_temp}°", win.colors.GREEN, int(win.width / 2) - 20, int(win.height / 2) + 30, 20)
    win.draw_text("|", win.colors.BLACK, int(win.width / 2), int(win.height / 2) + 30, 20)
    win.draw_text(f"{max_temp}°", win.colors.RED, int(win.width / 2) + 20, int(win.height / 2) + 30, 20)

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_presses = pygame.mouse.get_pressed()
            if mouse_presses[0]:
                if up_temp.collidepoint(event.pos):
                    new_temp += 0.5
                    win.draw_text(f'{new_temp}°', win.colors.BLACK, 300, int(win.height / 2), 20)
                if down_temp.collidepoint(event.pos):
                    new_temp -= 0.5
                    win.draw_text(f'{new_temp}°', win.colors.BLACK, 300, int(win.height / 2), 20)

    # TODO: review when we can safely trigger this, without crashing the display (aka display goes white)
    # if new_temp > temperature_data['temperature']:
    #     if not THERMOSTAT.get_relay_state(THERMOSTAT.cfg['relay_channel']):
    #         THERMOSTAT.relay_on(THERMOSTAT.cfg['relay_channel'])
    # if new_temp < temperature_data['temperature']:
    #     if THERMOSTAT.get_relay_state(THERMOSTAT.cfg['relay_channel']):
    #         THERMOSTAT.relay_off(THERMOSTAT.cfg['relay_channel'])
