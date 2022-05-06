#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# author: 'ACIOBANI'

try:
    import smbus2 as smbus
except ModuleNotFoundError as _:
    pass
import time

channel_array = [0b00000001, 0b00000010, 0b00000100, 0b00001000, 0b00010000, 0b00100000, 0b01000000, 0b10000000]


def change_multiplexer_channel(multiplexer, i2c_channel_setup):
    try:
        with smbus.SMBus(1) as bus:
            bus.write_byte(multiplexer, channel_array[i2c_channel_setup])
            time.sleep(0.01)
            # uncomment to debug
            print("TCA9548A I2C channel status:", bin(bus.read_byte(multiplexer)))
    except NameError as _:
        pass


if __name__ == '__main__':
    print("Now run i2cdetect")
