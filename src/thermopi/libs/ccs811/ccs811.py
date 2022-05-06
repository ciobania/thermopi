#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# author: 'ACIOBANI'
"""
/***************************************************
 * s-Sense CCS811 by itbrainpower.net python library v0.3 / 20200218
 * CCS811 TVOC/eCO2 sensors are manufactured by AMS
 *
 * This CCS811 CO2 and tVOC class - based on test software (Beerware license) provided by Nathan Seidle from SparkFun Electronics.
 * Thank you Nathan! Great job!
 * We've ported Nathan's functions into python, add some variables, functions and functionalities.
 *
 * This library it's compatible with:
 *	        s-Sense CCS811 I2C sensor breakout [PN: SS-CCS811#I2C, SKU: ITBP-6004], info https://itbrainpower.net/sensors/CCS811-CO2-TVOC-I2C-sensor-breakout
 *	        s-Sense CCS811 + HDC2010 I2C sensor breakout [PN: SS-HDC2010+CCS811#I2C, SKU: ITBP-6006], info https://itbrainpower.net/sensors/CCS811-HDC2010-CO2-TVOC-TEMPERATURE-HUMIDITY-I2C-sensor-breakout
 *	        all Raspberry PI, using Python 2.7
 *
 *
 *
 * CCS811 definitions are placed in ccs811_param.py
 *
 * New CCS811 sensors requires at 48-burn in. Once burned in a sensor requires 20 minutes of run in before readings are considered good.
 * READ CCS811 documentation! https://itbrainpower.net/downloadables/CCS811_DS000459_5-00.pdf
 *
 * You are legaly entitled to use this SOFTWARE ONLY IN CONJUNCTION WITH s-Sense CCS811 I2C sensors DEVICES USAGE. Modifications, derivates and redistribution
 * of this software must include unmodified this COPYRIGHT NOTICE. You can redistribute this SOFTWARE and/or modify it under the terms
 * of this COPYRIGHT NOTICE. Any other usage may be permited only after written notice of Dragos Iosub / R&D Software Solutions srl.
 *
 * This SOFTWARE is distributed is provide "AS IS" in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE.
 *
 *
 * itbrainpower.net invests significant time in design phase of our IoT products and in associated software and support resources.
 * Support us by purchasing our environmental and air quality sensors from here https://itbrainpower.net/order#s-Sense
 *
 * This library is dependent on python-smbus2
 *              https://pypi.org/project/smbus2/
 *              https://buildmedia.readthedocs.org/media/pdf/smbus2/latest/smbus2.pdf
 *
 * Dragos Iosub, Bucharest 2020.
 * https://itbrainpower.net
 */
"""


try:
    import smbus2 as smbus
    import RPi.GPIO as GPIO

    bus = smbus.SMBus(CHANNEL)
except ModuleNotFoundError as _:
    pass

from time import sleep

from thermopi.libs.ccs811.ccs811_param import *

CO2 = 0
tVOC = 0

HWRST = True  # hardware RESET pin defined
SleepWake = True  # SLEEP/WAKE pin defined


def ccs811GPIOInit():
    global CCS811_RESET_PIN
    global CCS811_WAKE_PIN
    global HWRST
    global SleepWake

    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    # GPIO.cleanup()
    print("Init CCS811 control GPIOs")

    try:
        GPIO.setup(CCS811_RESET_PIN, GPIO.IN)
    except:
        HWRST = False
        print("no RESET PIN defined")

    try:
        GPIO.setup(CCS811_WAKE_PIN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.output(CCS811_WAKE_PIN, GPIO.LOW)
    except:
        SleepWake = False
        print("no sleep wake control PIN defined")

    sleep(0.2)


def ccs811SWReset():
    global CO2
    global tVOC

    CO2 = 0
    tVOC = 0

    ccs811NWriteRegisters(CCS811_SW_RESET, [0x11, 0xE5, 0x72, 0x8A])
    sleep(0.5)


def ccs811HWReset():
    global HWRST
    global CO2
    global tVOC

    CO2 = 0
    tVOC = 0

    if HWRST == False:
        print("no RESET PIN defined")
        return

    GPIO.setup(CCS811_RESET_PIN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.output(CCS811_RESET_PIN, GPIO.LOW)  # RESET
    sleep(0.2)
    GPIO.setup(CCS811_RESET_PIN, GPIO.IN)  # release RESET line
    sleep(0.5)
    return


def ccs811Sleep():
    global SleepWake
    if (SleepWake == False):
        return
    GPIO.setup(CCS811_WAKE_PIN, GPIO.IN)


def ccs811Wake():
    global SleepWake
    if (SleepWake == False):
        return
    GPIO.setup(CCS811_WAKE_PIN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.output(CCS811_WAKE_PIN, GPIO.LOW)


def ccs811ReadNRegisters(address, length):
    global bus
    global CCS811_I2C_ADDRESS
    contents = bus.read_i2c_block_data(CCS811_I2C_ADDRESS, address, length)
    return contents


def ccs811ReadRegister(address):
    global bus
    global CCS811_I2C_ADDRESS

    contents = bus.read_i2c_block_data(CCS811_I2C_ADDRESS, address, 1)
    return contents[0]


def ccs811NWriteRegisters(address, data):
    global bus
    global CCS811_I2C_ADDRESS
    bus.write_i2c_block_data(CCS811_I2C_ADDRESS, address, data)


def ccs811WriteRegister(address, data):
    global bus
    global CCS811_I2C_ADDRESS

    bus.write_byte_data(CCS811_I2C_ADDRESS, address, data)


# Displays the type of error
# Calling this causes reading the contents of the ERROR register
# This should clear the ERROR_ID register
def ccs811PrintError():
    error = ccs811ReadRegister(CCS811_ERROR_ID)
    if (error & 1 << 5):
        print("Error: HeaterSupply ")
    if (error & 1 << 4):
        print("Error: HeaterFault ")
    if (error & 1 << 3):
        print("Error: MaxResistance ")
    if (error & 1 << 2):
        print("Error: MeasModeInvalid ")
    if (error & 1 << 1):
        print("Error: ReadRegInvalid")
    if (error & 1 << 0):
        print("Error: MsgInvalid ")


def ccs811CheckForError():
    value = ccs811ReadRegister(CCS811_STATUS)
    # print "STATUS register : 0x%02x " %value
    return value & 1 << 0


# Mode 0 = Idle
# Mode 1 = read every 1s
# Mode 2 = every 10s
# Mode 3 = every 60s
# Mode 4 = RAW mode
def ccs811SetDriveMode(mode):
    if (mode > 4):  # error correction
        mode = 4

    setting = ccs811ReadRegister(CCS811_MEAS_MODE)  # Read what's currently there
    setting &= ~(0b00000111 << 4)  # Clear DRIVE_MODE bits
    setting = setting | (mode << 4)  # Mask in mode
    ccs811WriteRegister(CCS811_MEAS_MODE, setting)


def ccs811AppValid():
    # print "AppValid to be done"
    value = ccs811ReadRegister(CCS811_STATUS)
    return (value & 1 << 4)


# Enable the nINT signal
def ccs811EnableInterrupts():
    setting = ccs811ReadRegister(CCS811_MEAS_MODE)  # Read what's currently there
    setting |= setting | (1 << 3)  # Set INTERRUPT bit
    ccs811WriteRegister(CCS811_MEAS_MODE, setting)


# Enable the nINT signal
def ccs811DisableInterrupts():
    setting = ccs811ReadRegister(CCS811_MEAS_MODE)  # Read what's currently there
    setting &= ~(1 << 3) & 0xFF  # Clear INTERRUPT bit
    ccs811WriteRegister(CCS811_MEAS_MODE, setting)


# Updates the total voltatile organic compounds (TVOC) in parts per billion (PPB)
# and the CO2 value
def ccs811ReadAlgorithmResults():
    global CO2
    global tVOC

    contents = ccs811ReadNRegisters(CCS811_ALG_RESULT_DATA, 4)

    co2MSB = contents[0]
    co2LSB = contents[1]
    tvocMSB = contents[2]
    tvocLSB = contents[3]

    CO2 = (co2MSB << 8) | co2LSB
    tVOC = (tvocMSB << 8) | tvocLSB


# Checks to see if DATA_READ flag is set in the status register
def ccs811DataAvailable():
    value = ccs811ReadRegister(CCS811_STATUS)
    return (value & 1 << 3)


def ccs811CheckDataAndUpdate():
    if (ccs811DataAvailable()):
        ccs811ReadAlgorithmResults()  # update the global tVOC and CO2 variables
        return True
    else:
        return False


def ccs811GetBaseline():
    global bus

    contents = ccs811ReadNRegisters(CCS811_BASELINE, 2)
    baselineMSB = contents[0]
    baselineLSB = contents[1]

    # print "baselineMSB: 0x%02x " %baselineMSB
    # print "baselineLSB: 0x%02x " %baselineLSB

    baseline = (baselineMSB << 8) | baselineLSB
    return baseline


def ccs811Begin(driveMode):
    global HWRST
    global SleepWake

    ccs811GPIOInit()

    if (HWRST != False):
        ccs811HWReset()
    else:
        print("sofware reset")
        ccs811SWReset()

    ccs811Wake()

    contents = ccs811ReadRegister(CCS811_HW_ID)  # Hardware ID should be 0x81
    print("CCS811_HW_ID : 0x%02x " % contents)

    if (contents != 0x81):  # "CCS811 not found. Please check wiring."
        print("CCS811 not found. Please check wiring.")
        # return -1
    else:
        print("CCS811 found.")

    if (ccs811CheckForError() == True):
        print("Error at startup")
        ccs811PrintError()
        # return -2
    else:
        print("Clean startup")

    if (ccs811AppValid() == False):
        print("Error: App not valid.")
        # return -3
    else:
        print("App valid")

    bus.write_byte(CCS811_I2C_ADDRESS, CCS811_APP_START)

    if (ccs811CheckForError() == True):
        print("Error at AppStart")
        ccs811PrintError()
        # return -4
    else:
        print("Clean AppStart")

    ccs811DisableInterrupts()

    ccs811SetDriveMode(driveMode)  # Mode 0/1/2/3/4==> Idle/1sec/10sec/60sec/RAW	        ITBP add

    # sleep(0.5)

    if (ccs811CheckForError() == True):
        print("Error at SetDriveMode")
        ccs811PrintError()
        # return -5
    else:
        print("Clean SetDriveMode")

    result = ccs811GetBaseline()
    print("baseline for this sensor: 0x%02x " % result)
    return 0


def ccs811SetEnvironmentalData(relativeHumidity, temperature):
    rH = int(relativeHumidity * 1000)
    temp = int(temperature * 1000)

    if ((rH % 1000) / 100) > 7:
        envData0 = (rH / 1000 + 1) << 1
    else:
        envData0 = int((rH / 1000)) << 1

    envData1 = 0  # CCS811 only supports increments of 0.5 so bits 7-0 will always be zero

    if ((((rH % 1000) / 100) > 2) and (((rH % 1000) / 100) < 8)):
        envData0 = envData0 | 1  # Set 9th bit of fractional to indicate 0.5%

    temp = temp + 25000  # Add the 25C offset

    # Split value into 7-bit integer and 9-bit fractional
    if ((temp % 1000) / 100) > 7:
        envData2 = int((temp / 1000 + 1)) << 1
    else:
        envData2 = int((temp / 1000)) << 1

    envData3 = 0

    if (((temp % 1000) / 100) > 2 and (((temp % 1000) / 100) < 8)):
        envData2 |= envData2 | 1  # Set 9th bit of fractional to indicate 0.5C

    envData = [envData0, envData1, envData2, envData3]

    # bus.write_i2c_block_data(CCS811_I2C_ADDRESS, CCS811_ENV_DATA, envData)
    ccs811NWriteRegisters(CCS811_ENV_DATA, envData)


def ccs811GetCO2():
    global CO2
    return CO2


def ccs811GetTVOC():
    global tVOC
    return tVOC


# Initialize I2C (SMBus)
try:
    configContents = ccs811ReadRegister(CCS811_HW_ID)
    print("I2C already loaded")
except (Exception, ) as _:
    print(f"In exception SMBus: {_}")
