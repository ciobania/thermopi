#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# author: 'ACIOBANI'
"""
s-Sense CCS811 by itbrainpower.net I2C sensor breakout example - v1.0/20200218.

Compatible with:
        s-Sense CCS811 I2C sensor breakout [PN: SS-CCS811#I2C, SKU: ITBP-6004], info https://itbrainpower.net/sensors/CCS811-CO2-TVOC-I2C-sensor-breakout
        s-Sense CCS811 + HDC2010 I2C sensor breakout [PN: SS-HDC2010+CCS811#I2C, SKU: ITBP-6006], info https://itbrainpower.net/sensors/CCS811-HDC2010-CO2-TVOC-TEMPERATURE-HUMIDITY-I2C-sensor-breakout
        all Raspberry PI, using Python 2.7

Reading CO2 and tVOC values example (pulling at 2sec) - based on test software (Beerware license) written by Nathan Seidle from SparkFun Electronics.
Thank you Nathan! Great job!

We've ported Nathan's functions into python, add some variables, functions and functionalities.


Mandatory wiring [bellow for RPi B/B+/II/3B/3B+/4/Zero/Zero W]:
        - sensor Vin            <------> RPI pin 1 [3V3 power] *
        - sensor I2C SDA        <------> RPI pin 3 [i2c-1 SDA]
        - sensor I2C SCL        <------> RPI pin 5 [i2c-1 SCL]
        - sensor GND            <------> RPI pin 9 [GND]
        - sensor PAD6 [!WAKE]   <------> RPI pin 6 [GND] ** or RPI pin 22 [GPIO25] ***

Optional wiring:
        - sensor PAD7 [!RESET]  <------> RPI pin 7 [GPIO4] ****

Wiring notes:
        *    to spare 3V3 power - read about RPI I2C sensors 5V powering
        **   if connected to GND, CCS811 will be always WAKE
        ***  if connected to RPI pin 22, CCS811 can be switched in WAKE/SLEEP mode - handled inside library
        **** if RESET is not conneted, only CCS811 software reset will be available in application.
        common ==> check ccs811_param.py file for WAKE and RESET options!

WIRING WARNING:
        Wrong wiring may damage your RaspberryPI or your sensor! Double check what you've done.


IMPORTANT INFO:
        New CCS811 sensors requires 48 hours burn in. After that readings should be considered good after 20 minutes of running.


CCS811 definitions are placed in ccs811_param.py


Bellow, how to set-up i2c on RPi and install requiered python packages and other utilities.

Enable I2C channel 1
        a. sudo raspi-config
                menu F5	=> 	enable I2C
                save, exit and reboot.


        b. edit /boot/config.txt and add/enable following directives:
               dtparam=i2c_arm=on
               dtparam=i2c_arm_baudrate=10000

           save and reboot.

Check i2c is loaded:
        run: ls /dev/*i2c*
        should return: /dev/i2c-1

Add i2c-tools packages:
        sudo apt-get install -y i2c-tools

Check sensor I2C connection:
        run: i2cdetect -y 1
        you should see listed the s-Sense CCS811 I2C address [0x5A]

Install additional python packages:
        a. sudo apt-get install python-setuptools
        b. wget https://files.pythonhosted.org/packages/6a/06/80a6928e5cbfd40c77c08e06ae9975c2a50109586ce66435bd8166ce6bb3/smbus2-0.3.0.tar.gz
        c. expand archive
        d. chdir smbus2-0.3.0
        e. sudo python setup.py install


You are legaly entitled to use this SOFTWARE ONLY IN CONJUNCTION WITH s-Sense CCS811 I2C sensors DEVICES USAGE. Modifications, derivates and redistribution
of this software must include unmodified this COPYRIGHT NOTICE. You can redistribute this SOFTWARE and/or modify it under the terms
of this COPYRIGHT NOTICE. Any other usage may be permited only after written notice of Dragos Iosub / R&D Software Solutions srl.

This SOFTWARE is distributed is provide "AS IS" in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.


itbrainpower.net invests significant time in design phase of our IoT products and in associated software and support resources.
Support us by purchasing our environmental and air quality sensors from here https://itbrainpower.net/order#s-Sense


Dragos Iosub, Bucharest 2020.
https://itbrainpower.net
"""

from libs.tca9548a import tca9548a
from ccs811 import *

tca9548a.change_multiplexer_channel(0x70, 1)
ccs811Begin(CCS811_driveMode_1sec)  # start CCS811, data update rate at 1sec

while 1:
    ccs811SetEnvironmentalData(21.102, 57.73)  # replace with temperature and humidity values from HDC2010 sensor

    if ccs811CheckDataAndUpdate():
        CO2 = ccs811GetCO2()
        tVOC = ccs811GetTVOC()
        print("CO2 : %d ppm" % CO2)
        print("tVOC : %d ppb" % tVOC)
    elif ccs811CheckForError():
        ccs811PrintError()

    sleep(2)
