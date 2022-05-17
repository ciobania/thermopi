#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# author: 'ACIOBANI'
import os
from datetime import datetime
from time import sleep
import yaml

from thermopi import CFG_DIR

from thermopi.libs.bme280.bme280 import read_chip_id, read_all_values
from thermopi.libs.ccs811.ccs811 import ccs811Begin, ccs811SetEnvironmentalData, ccs811CheckDataAndUpdate, ccs811GetCO2, \
    ccs811GetTVOC, ccs811CheckForError, ccs811PrintError
from thermopi.libs.ccs811.ccs811_param import CCS811_driveMode_1sec
from thermopi.libs.relay.relay import relay_setup, relay_on, relay_off, get_relay_state
from thermopi.libs.tca9548a import tca9548a


def get_thermostat_data():
    tca9548a.change_multiplexer_channel(0x70, 0)
    chip_id, chip_version = read_chip_id()
    print("Chip ID     :", chip_id)
    print("Version     :", chip_version)

    temperature, pressure, humidity = read_all_values()
    # print("Temperature : ", temperature, "C")
    # print("Pressure : ", pressure, "hPa")
    # print("Humidity : ", humidity, "%")
    return {'temperature': temperature, 'pressure': pressure, 'humidity': humidity}


def get_air_quality_data():
    thermostat_data = get_thermostat_data()

    tca9548a.change_multiplexer_channel(0x70, 1)
    ccs811Begin(CCS811_driveMode_1sec)  # start CCS811, data update rate at 1sec
    while 1:
        try:
            ccs811SetEnvironmentalData(temperature=thermostat_data['temperature'],
                                       relativeHumidity=int(thermostat_data['humidity']))

            if ccs811CheckDataAndUpdate():
                co2 = ccs811GetCO2()
                t_voc = ccs811GetTVOC()
                print("CO2 : %d ppm" % co2)
                print("tVOC : %d ppb" % t_voc)
            elif ccs811CheckForError():
                ccs811PrintError()

            sleep(2)
        except Exception as _:
            print("error happened", _)


get_thermostat_data()
# get_air_quality_data()

if __name__ == "__main__":
    status_msg = "Turned {} at time: {} with temperature: {} and humidity: {}"
    cfg = yaml.safe_load(open(os.path.join(CFG_DIR, 'thermostat_cfg.yaml'), 'r'))
    schedule = yaml.safe_load(open(os.path.join(CFG_DIR, 'schedule.yaml'), 'r'))
    relay_setup(cfg['relay_channel'])
    while True:
        temp_data = get_thermostat_data()
        min_temp = schedule['all_week']['interval'][0]['general_temp']['min']
        max_temp = schedule['all_week']['interval'][0]['general_temp']['max']
        if temp_data['temperature'] < min_temp:
            if not get_relay_state(cfg['relay_channel']):
                relay_on(cfg['relay_channel'])
                print(status_msg.format('ON',
                                        datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                                        temp_data['temperature'],
                                        temp_data['humidity']))
        elif min_temp < temp_data['temperature'] <= max_temp or temp_data['temperature'] > max_temp:
            if get_relay_state(cfg['relay_channel']):
                relay_off(cfg['relay_channel'])
                print(status_msg.format('OFF',
                                        datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                                        temp_data['temperature'],
                                        temp_data['humidity']))
        sleep(900)
