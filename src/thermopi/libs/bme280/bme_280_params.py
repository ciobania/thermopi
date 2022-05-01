#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# author: 'ACIOBANI'

DEVICE_I2C_ADDRESS = 0x76  # Default device I2C address

REG_ID = 0xD0
# Register Addresses
REG_DATA = 0xF7
REG_CONTROL = 0xF4
REG_CONFIG = 0xF5

REG_CONTROL_HUM = 0xF2
REG_HUM_MSB = 0xFD
REG_HUM_LSB = 0xFE

# Oversample setting - page 27
OVERSAMPLE_TEMP = 2
OVERSAMPLE_PRES = 2
MODE = 1

# Oversample setting for humidity register - page 26
OVERSAMPLE_HUM = 2
