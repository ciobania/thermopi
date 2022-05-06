import os
import sys

import pygame
import pygame_widgets


def scheduler(win):
    run_clock = True

    while run_clock:
        win.draw_menu()
        win.screen_update()
        pen_down = False

        win.draw_text("scheduler", (0, 0, 0), 60, 130, 20)

        events = pygame.event.get()
        if win.drop_down.getSelected() == 1:
            win.draw_text("home", (0, 0, 0), 60, 130, 20)
        elif win.drop_down.getSelected() == 2:
            win.draw_text("scheduler", (0, 0, 0), 60, 130, 20)
        elif win.drop_down.getSelected() == 3:
            win.draw_text("settings", (0, 0, 0), 60, 130, 20)
        elif win.drop_down.getSelected() == 'restart':
            print(f'Restarting with sys.argv:: {sys.argv}')
            os.execv(sys.executable, ['python3'] + sys.argv)

        pygame_widgets.update(events)
        pygame.display.update()
        # check_display_light_status(pen_down)
