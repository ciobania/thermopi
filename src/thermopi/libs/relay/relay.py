#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# author: 'ACIOBANI'
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)


def get_relay_state(channel):
    return GPIO.input(channel)


def relay_setup(channel):
    # GPIO setup
    GPIO.setup(channel, GPIO.OUT)


def relay_on(pin):
    GPIO.output(pin, GPIO.HIGH)


def relay_off(pin):
    GPIO.output(pin, GPIO.LOW)


if __name__ == '__main__':
    try:
        relay_on(23)
        time.sleep(30)
        relay_off(23)
        time.sleep(30)
    except KeyboardInterrupt as _:
        GPIO.cleanup()
        pass
