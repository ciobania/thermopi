#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# author: 'ACIOBANI'

# I2C channel used
CHANNEL = 1  # /dev/i2c-1

#  CCS811 defaults to address 0x5A
CCS811_I2C_ADDRESS = 0x5A  # alt address 0x5B

# remove comment from line bellow in order to enable sensor HARDWARE reset
# CCS811_RESET_PIN = 7                        #GPIO connected to !RESET pin      [GPIO.BOARD numbering]

# leave bellow line comments if you connect s-Sense CCS881 pad 6 to RPI GND
# CCS811_WAKE_PIN = 22                        #GPIO connected to !WAKE pin       [GPIO.BOARD numbering]


"""do not change definitions bellow"""

#  Constants for setting measurement time mode
CCS811_driveMode_Idle = 0
CCS811_driveMode_1sec = 1
CCS811_driveMode_10sec = 2
CCS811_driveMode_60sec = 3
CCS811_driveMode_RAW = 4

#  Define CCS811 Register Map
CCS811_STATUS = 0x00
CCS811_MEAS_MODE = 0x01
CCS811_ALG_RESULT_DATA = 0x02
CCS811_RAW_DATA = 0x03
CCS811_ENV_DATA = 0x05
CCS811_NTC = 0x06
CCS811_THRESHOLDS = 0x10
CCS811_BASELINE = 0x11
CCS811_HW_ID = 0x20
CCS811_HW_VERSION = 0x21
CCS811_FW_BOOT_VERSION = 0x23
CCS811_FW_APP_VERSION = 0x24
CCS811_ERROR_ID = 0xE0
CCS811_APP_START = 0xF4
CCS811_SW_RESET = 0xFF
