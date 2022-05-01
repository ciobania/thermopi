#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# author: 'ACIOBANI'

# --------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#           bme280.py
#  Read data from a digital pressure sensor.
#
#  Official datasheet available from :
#  https://www.bosch-sensortec.com/bst/products/all_products/bme280
#
# Author : Matt Hawkins
# Date   : 21/01/2018
#
# https://www.raspberrypi-spy.co.uk/
#
# --------------------------------------
import math
from datetime import datetime

import smbus2 as smbus
import time
from ctypes import c_short

from thermopi.libs.bme280.bme_280_params import *
from thermopi.libs.tca9548a import tca9548a

bus = smbus.SMBus(1)  # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1


def set_temp_offset(value):
    """
    Set temperature offset in celsius.
    If set, the temperature t_fine will be increased by given value in celsius.
    :param value: Temperature offset in Celsius, eg. 4, -8, 1.25
    """
    if value == 0:
        offset_temp_in_t_fine = 0
    else:
        offset_temp_in_t_fine = int(math.copysign((((int(abs(value) * 100)) << 8) - 128) / 5, value))
    return offset_temp_in_t_fine


def get_signed_short(data, index):
    # return two bytes from data as a signed 16-bit value
    return c_short((data[index + 1] << 8) + data[index]).value


def get_unsigned_short(data, index):
    # return two bytes from data as an unsigned 16-bit value
    return (data[index + 1] << 8) + data[index]


def get_signed_char(data, index):
    # return one byte from data as a signed char
    result = data[index]
    if result > 127:
        result -= 256
    return result


def get_unsigned_char(data, index):
    # return one byte from data as an unsigned char
    result = data[index] & 0xFF
    return result


def get_calibration_data(address):
    # Read blocks of calibration data from EEPROM
    # See Page 22 data sheet
    cal1 = bus.read_i2c_block_data(address, 0x88, 24)
    cal2 = bus.read_i2c_block_data(address, 0xA1, 1)
    cal3 = bus.read_i2c_block_data(address, 0xE1, 7)
    return cal1, cal2, cal3


def get_temperature_byte_data(cal1):
    # Convert byte data to word values
    dig_t1 = get_unsigned_short(cal1, 0)
    dig_t2 = get_signed_short(cal1, 2)
    dig_t3 = get_signed_short(cal1, 4)
    return dig_t1, dig_t2, dig_t3


def get_pressure_byte_data(cal1):
    dig_p1 = get_unsigned_short(cal1, 6)
    dig_p2 = get_signed_short(cal1, 8)
    dig_p3 = get_signed_short(cal1, 10)
    dig_p4 = get_signed_short(cal1, 12)
    dig_p5 = get_signed_short(cal1, 14)
    dig_p6 = get_signed_short(cal1, 16)
    dig_p7 = get_signed_short(cal1, 18)
    dig_p8 = get_signed_short(cal1, 20)
    dig_p9 = get_signed_short(cal1, 22)
    return dig_p1, dig_p2, dig_p3, dig_p4, dig_p5, dig_p6, dig_p7, dig_p8, dig_p9


def get_humidity_byte_data(cal2, cal3):
    dig_h1 = get_unsigned_char(cal2, 0)
    dig_h2 = get_signed_short(cal3, 0)
    dig_h3 = get_unsigned_char(cal3, 2)

    dig_h4 = get_signed_char(cal3, 3)
    dig_h4 = (dig_h4 << 24) >> 20
    dig_h4 = dig_h4 | (get_signed_char(cal3, 4) & 0x0F)

    dig_h5 = get_signed_char(cal3, 5)
    dig_h5 = (dig_h5 << 24) >> 20
    dig_h5 = dig_h5 | (get_unsigned_char(cal3, 4) >> 4 & 0x0F)

    dig_h6 = get_signed_char(cal3, 6)
    return dig_h1, dig_h2, dig_h3, dig_h4, dig_h5, dig_h6


def get_raw_temperature(data, dig_t1, dig_t2, dig_t3):
    # Refine temperature
    temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
    var1 = (((temp_raw >> 3) - (dig_t1 << 1)) * dig_t2) >> 11
    var2 = (((((temp_raw >> 4) - dig_t1) * ((temp_raw >> 4) - dig_t1)) >> 12) * dig_t3) >> 14

    t_fine = var1 + var2  # + set_temp_offset(2.129)
    return t_fine


def read_temperature(t_fine):
    temperature = float(((t_fine * 5) + 128) >> 8)
    return temperature


def read_chip_id(address=DEVICE_I2C_ADDRESS):
    # Chip ID Register Address
    (chip_id, chip_version) = bus.read_i2c_block_data(address, REG_ID, 2)
    return chip_id, chip_version


def read_all_values(address=DEVICE_I2C_ADDRESS):
    bus.write_byte_data(address, REG_CONTROL_HUM, OVERSAMPLE_HUM)
    control = OVERSAMPLE_TEMP << 5 | OVERSAMPLE_PRES << 2 | MODE
    bus.write_byte_data(address, REG_CONTROL, control)

    cal1, cal2, cal3 = get_calibration_data(address)

    dig_t1, dig_t2, dig_t3 = get_temperature_byte_data(cal1)
    dig_p1, dig_p2, dig_p3, dig_p4, dig_p5, dig_p6, dig_p7, dig_p8, dig_p9 = get_pressure_byte_data(cal1)
    dig_h1, dig_h2, dig_h3, dig_h4, dig_h5, dig_h6 = get_humidity_byte_data(cal2, cal3)

    # Wait in ms (Datasheet Appendix B: Measurement time and current calculation)
    wait_time = 1.25 + (2.3 * OVERSAMPLE_TEMP) + ((2.3 * OVERSAMPLE_PRES) + 0.575) + ((2.3 * OVERSAMPLE_HUM) + 0.575)
    time.sleep(wait_time / 1000)  # Wait the required time

    # Read temperature/pressure/humidity
    data = bus.read_i2c_block_data(address, REG_DATA, 8)
    pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
    hum_raw = (data[6] << 8) | data[7]

    t_fine = get_raw_temperature(data, dig_t1, dig_t2, dig_t3)
    temperature = read_temperature(t_fine)

    # Refine pressure and adjust for temperature
    var1 = t_fine / 2.0 - 64000.0
    var2 = var1 * var1 * dig_p6 / 32768.0
    var2 = var2 + var1 * dig_p5 * 2.0
    var2 = var2 / 4.0 + dig_p4 * 65536.0
    var1 = (dig_p3 * var1 * var1 / 524288.0 + dig_p2 * var1) / 524288.0
    var1 = (1.0 + var1 / 32768.0) * dig_p1
    if var1 == 0:
        pressure = 0
    else:
        pressure = 1048576.0 - pres_raw
        pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
        var1 = dig_p9 * pressure * pressure / 2147483648.0
        var2 = pressure * dig_p8 / 32768.0
        pressure = pressure + (var1 + var2 + dig_p7) / 16.0

    # Refine humidity
    humidity = t_fine - 76800.0
    humidity = (hum_raw - (dig_h4 * 64.0 + dig_h5 / 16384.0 * humidity)) * (
            dig_h2 / 65536.0 * (1.0 + dig_h6 / 67108864.0 * humidity * (1.0 + dig_h3 / 67108864.0 * humidity)))
    humidity = humidity * (1.0 - dig_h1 * humidity / 524288.0)
    if humidity > 100:
        humidity = 100
    elif humidity < 0:
        humidity = 0

    return temperature / 100.0, pressure / 100.0, humidity


def main():
    print_msg = '| {:0<11} | {:>23}{} |'
    tca9548a.change_multiplexer_channel(0x70, 0)
    chip_id, chip_version = read_chip_id()

    temperature, pressure, humidity = read_all_values()
    time_now = str(datetime.now())[:23]
    status_data = {"Chip ID": {'value': chip_id, 'measurement_unit': ''},
                   "Version": {'value': chip_version, 'measurement_unit': ''},
                   "Temperature": {'value': temperature, 'measurement_unit': 'C'},
                   "Pressure": {'value': pressure, 'measurement_unit': 'hPa'},
                   "Humidity": {'value': humidity, 'measurement_unit': '%'},
                   "Date": {"value": time_now, 'measurement_unit': ''}}
    for metric_stat, metric_data in status_data.items():
        print(print_msg.format(metric_stat, *metric_data.values()))


if __name__ == "__main__":
    main()
