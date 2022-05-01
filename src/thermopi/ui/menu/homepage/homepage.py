import datetime
import os
import pygame
import pygame_widgets
import sys
import socket
import subprocess

from datetime import timedelta
from time import time, monotonic

from pygame_widgets.dropdown import Dropdown
from thermopi import FONTS_DIR, IMAGES_DIR
from thermopi.libs.ili9341.geometry import is_inside_polygon

try:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(5, GPIO.OUT)
except ModuleNotFoundError as _:
    GPIO = None

# os.environ["SDL_WINDOWID"] = ":0.0"
# os.environ["SDL_VIDEODRIVER"] = "X11"
os.environ["SDL_FBDEV"] = "/dev/fb1"
# os.environ["DISPLAY"] = ":0.0"
# Comment out for now, as this is causing erratic behaviour with the mouse and event0
# os.environ['SDL_MOUSEDRV'] = 'libinput'
# os.environ['SDL_MOUSEDEV'] = '/dev/input/event0'

# Initialize pygame
WIDTH = 320
HEIGHT = 240
SCREEN_RECT = pygame.Rect(0, 0, WIDTH, HEIGHT)

if pygame.get_sdl_version()[0] == 2:
    pygame.mixer.pre_init(44100, 32, 2, 1024)
pygame.init()
if pygame.mixer and not pygame.mixer.get_init():
    print("Warning, no sound")
    pygame.mixer = None

# Set display mode
fullscreen = True
# Set the display mode
best_depth = pygame.display.mode_ok(SCREEN_RECT.size, pygame.NOFRAME, 32)
screen = pygame.display.set_mode(SCREEN_RECT.size, pygame.NOFRAME, best_depth)

LED_PIN = 5
PEN_PIN = 26
if GPIO:

    # To read the state
    state = GPIO.input(5)
    msg = "Display LED is: {}"
    if state:
        print(msg.format('on'))
    else:
        print(msg.format('off'))

RED = (135, 62, 35)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WIN_BLUE = (59, 119, 188)


pygame.display.set_caption("ThermoPi")
pygame.mouse.set_visible(False)

font_path = os.path.join(FONTS_DIR, 'FreeSerifItalic.ttf')

START_TIME = time()


def draw_text(text, text_col, x, y, font_size=0, center=1, bold=False, italic=False):
    # change font size here or use a different font?
    text_font = pygame.font.SysFont(font_path, font_size,
                                    bold=bold,
                                    italic=italic)
    img = text_font.render(text, True, text_col)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    screen.blit(img, rect)


def draw_up_temp_button(x, y):
    return _draw_arrow_button(x, y, 180)


def draw_down_temp_button(x, y):
    return _draw_arrow_button(x, y, 0)


def _draw_arrow_button(x, y, angle):
    _arrow_png_path = os.path.join(IMAGES_DIR, 'arrow.png')
    _arrow = pygame.image.load(_arrow_png_path)
    _arrow = pygame.transform.scale(_arrow, (40, 40))
    _arrow = pygame.transform.rotate(_arrow, angle)
    return screen.blit(_arrow, (x, y))  # x, y coordinates


def draw_button(text, x, y):
    # light shade of the button
    color_light = (170, 170, 170)
    # dark shade of the button
    color_dark = (100, 100, 100)
    button_font = pygame.font.SysFont(font_path,
                                      20,
                                      bold=False)
    text = button_font.render(text, True, color_light)
    rect = pygame.draw.rect(screen, color_dark, [x, y, 80, 40])
    screen.blit(text, (int(rect.center[0] - text.get_size()[0] / 2),
                       int(rect.center[1] - text.get_size()[1] / 2)))


def draw_bg():
    screen.fill(WIN_BLUE)


def draw_time(x, y):
    str_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    draw_text(str_time, BLACK, x, y, 20)


def draw_menu():
    menu_choices = ["HOME", "SCHEDULER", "SETTINGS"]
    # light shade of the button
    color_light = (170, 170, 170)
    # dark shade of the button
    color_dark = (100, 100, 100)
    dropdown = Dropdown(screen, 0, 0, 80, 40,
                        name='MENU',
                        choices=menu_choices,
                        borderRadius=0,
                        colour=pygame.Color(color_light),
                        textColour=pygame.Color(color_dark),
                        textHAlign='centre',
                        values=[1, 2, 3],
                        direction='down')
    dropdown.draw()
    return dropdown


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


def _get_surface_polygon(surface):
    attrs = ('topleft', 'topright', 'bottomright', 'bottomleft')
    return [getattr(surface, attr) for attr in attrs]


def get_pi_temp():
    result = subprocess.check_output('/usr/bin/vcgencmd measure_temp',
                                     shell=True,
                                     universal_newlines=True)
    temp = result.strip().replace('\'', chr(176))[5:]
    return temp


pygame.event.set_allowed([pygame.MOUSEBUTTONDOWN, pygame.QUIT])


def settings():
    run_clock = True

    menu = draw_menu()
    while run_clock:
        pen_down = False

        draw_bg()
        draw_time(65, 230)
        host_name = socket.gethostname()
        ip_address = socket.gethostbyname(host_name)
        draw_text(f"HOSTNAME: {host_name}", BLACK, 80, 100, 20)
        draw_text(f"IP: {ip_address}", BLACK, 60, 130, 20)
        draw_text(f"UPTIME: {timedelta(seconds=monotonic())}", BLACK, 60, 160, 20)
        draw_text(f"TEMP: {get_pi_temp()}", BLACK, 60, 180, 20)

        events = pygame.event.get()
        selected_menu = menu.getSelected()
        if selected_menu == 1:
            main()
        elif selected_menu == 2:
            scheduler()

        pygame_widgets.update(events)
        pygame.display.update()
        check_display_light_status(pen_down)


def scheduler():
    run_clock = True

    menu = draw_menu()
    while run_clock:
        pen_down = False

        draw_bg()
        draw_time(65, 230)

        draw_text("scheduler", BLACK, 60, 130, 20)

        events = pygame.event.get()
        selected_menu = menu.getSelected()
        if selected_menu == 1:
            main()
        elif selected_menu == 3:
            settings()

        pygame_widgets.update(events)
        pygame.display.update()
        check_display_light_status(pen_down)


def main():
    run_clock = True

    new_temp = 20
    menu = draw_menu()

    while run_clock:
        pen_down = False

        draw_bg()
        draw_time(65, 230)

        up_temp = draw_up_temp_button(280, int(HEIGHT / 2) - 60)
        draw_text(f'{new_temp}°', BLACK, 300, int(HEIGHT / 2), 20)
        down_temp = draw_down_temp_button(280, int(HEIGHT / 2) + 20)
        draw_text('L: 21°', BLACK, 20, 100, 20)
        draw_text('M: 22°', BLACK, 20, 130, 20)
        draw_text('S: 23°', BLACK, 20, 160, 20)
        draw_text('23°', WHITE, int(WIDTH / 2), int(HEIGHT / 2), 60)
        draw_text('22.5°', GREEN, int(WIDTH / 2) - 20, int(HEIGHT / 2) + 30, 20)
        draw_text('|', BLACK, int(WIDTH / 2), int(HEIGHT / 2) + 30, 20)
        draw_text('23.5°', RED, int(WIDTH / 2) + 20, int(HEIGHT / 2) + 30, 20)

        selected_menu = menu.getSelected()
        if selected_menu == 2:
            scheduler()
        elif selected_menu == 3:
            settings()

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run_clock = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_presses = pygame.mouse.get_pressed()
                if mouse_presses[0]:
                    pen_down = True

                    if up_temp.collidepoint(event.pos):
                        new_temp += 0.5
                        draw_text(f'{new_temp}°', BLACK, 300, int(HEIGHT / 2), 20)
                    if down_temp.collidepoint(event.pos):
                        new_temp -= 0.5
                        draw_text(f'{new_temp}°', BLACK, 300, int(HEIGHT / 2), 20)

        pygame_widgets.update(events)
        pygame.display.update()
        check_display_light_status(pen_down)


main()
pygame.quit()
sys.exit()
