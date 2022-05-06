import os
from datetime import datetime

import pygame
from pygame_widgets.dropdown import Dropdown

from thermopi.ui.helpers.helpers import DisplayBgrColor

from thermopi import FONTS_DIR

FONT_PATH = os.path.join(FONTS_DIR, 'FreeSerifItalic.ttf')


class Screen:
    def __init__(self, screen, title, width=None, height=None, fill=(0, 0, 0)):
        self.title = title
        self.width = width
        self.height = height
        self.fill = fill
        self.current = False
        self.screen = screen
        self.drop_down = 1
        self.colors = DisplayBgrColor

    def make_current(self):
        pygame.display.set_caption(self.title)
        self.current = 1
        self.draw_menu()

        return self

    def end_current(self):
        self.current = False

    def check_update(self):
        return self.current

    def screen_update(self):
        self.screen.fill(DisplayBgrColor.WIN_BLUE)
        self.draw_time(65, 230)

    def draw_bg(self):
        self.screen_update()

    def draw_text(self, text, text_col, x, y, font_size=0, center=1, bold=False, italic=False):
        # change font size here or use a different font?
        text_font = pygame.font.SysFont(FONT_PATH,
                                        font_size,
                                        bold=bold,
                                        italic=italic)
        img = text_font.render(text, True, text_col)
        rect = img.get_rect()
        if center:
            rect.center = (x, y)
        self.screen.blit(img, rect)

    def draw_time(self, x=65, y=230):
        str_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.draw_text(str_time,
                       DisplayBgrColor.WHITE,
                       x, y, 20)

    def draw_menu(self):
        menu_choices = ["HOME", "SCHEDULER", "SETTINGS", "RESTART"]
        # light shade of the button
        color_light = (170, 170, 170)
        # dark shade of the button
        color_dark = (100, 100, 100)
        dropdown = Dropdown(self.screen, 0, 0, 80, 40,
                            name='MENU',
                            choices=menu_choices,
                            borderRadius=0,
                            colour=pygame.Color(color_light),
                            textColour=pygame.Color(color_dark),
                            textHAlign='centre',
                            values=[1, 2, 3, 'restart'],
                            direction='down')
        self.drop_down = dropdown
