#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# author: 'ACIOBANI'
from thermopi import LOGGER, LOG
from time import time
from twisted.internet import reactor, task, endpoints, defer

from endpoints import *
from factories.finger_factory import FingerFactory
from libs.thermostat.thermostat import Thermostat
from ui.menu.homepage.homepage_old import init, modify_temp, start_time, TFT
# from twisted.logger import Logger
# LOG = Logger()


init()

thermostat = Thermostat()


def get_temp_data_and_update_display_callback():
    """
    Called at every loop interval.
    """
    temp_data = thermostat.get_thermostat_data()
    modify_temp(temp_data['temperature'])

    return


def check_screen_light():
    global start_time
    now_time = time()
    if now_time - start_time > 30 and not TFT.light_status:
        TFT.back_light(True)
        LOG.info("PEN_UP: start_time, now_time: {} {} {}".format(start_time, now_time, TFT.light_status))

    if TFT.pen_down():
        start_time = time()
        if TFT.light_status:
            TFT.back_light(False)
        LOG.info("PEN_DOWN: start_time, now_time: {} {} {}".format(start_time, now_time, TFT.light_status))
    return


screen_light_loop = task.LoopingCall(check_screen_light)
# Start looping every half a second.
screen_light_deferred_loop = screen_light_loop.start(0.5)

get_temp_data_loop = task.LoopingCall(get_temp_data_and_update_display_callback)
# Start looping every 2 minutes.
temp_data_deferred_loop = get_temp_data_loop.start(90)

task_run_thermostat = task.LoopingCall(thermostat.run)
task_run_thermostat.start(300, True)

fingerEndpoint = endpoints.serverFromString(reactor, "tcp:9000:interface=192.168.1.140")
fingerEndpoint.listen(FingerFactory({b"adrian": b"Happy and well"}))
reactor.run()
