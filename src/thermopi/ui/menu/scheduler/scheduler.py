
def scheduler(win):
    print('scheduler')
    # win.draw_menu()
    win.draw_text("scheduler", (0, 0, 0), 60, 130, 20)

    # run_clock = True

    # while run_clock:
    #     win.draw_menu()
    #     win.screen_update()
    #     pen_down = False
    #
    #     # if win.drop_down.getSelected() == 1:
    #     #     win.draw_text("home", (0, 0, 0), 60, 130, 20)
    #     # elif win.drop_down.getSelected() == 2:
    #     #     win.draw_text("scheduler", (0, 0, 0), 60, 130, 20)
    #     # elif win.drop_down.getSelected() == 3:
    #     #     win.draw_text("settings", (0, 0, 0), 60, 130, 20)
    #     # elif win.drop_down.getSelected() == 'restart':
    #     #     print(f'Restarting with sys.argv:: {sys.argv}')
    #     #     os.execv(sys.executable, ['python3'] + sys.argv)
