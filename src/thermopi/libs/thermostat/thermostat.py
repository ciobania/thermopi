#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# author: 'ACIOBANI'
import os
import yaml
import time

from datetime import datetime

from thermopi import CFG_DIR, LOGGER
from thermopi.libs.bme280.bme280 import read_chip_id, read_all_values
from thermopi.libs.ccs811.ccs811 import CCS811
from thermopi.libs.relay.relay import relay_setup, relay_on, relay_off, get_relay_state
from thermopi.libs.tca9548a import tca9548a


class Thermostat:

    def __init__(self, start_time=datetime.now()):
        self.status_msg = "Turned {} at time: {} with temperature: {} and humidity: {}"
        self.cfg = yaml.safe_load(open(os.path.join(CFG_DIR, 'thermostat_cfg.yaml'), 'r'))
        self.schedule = yaml.safe_load(open(os.path.join(CFG_DIR, 'schedule.yaml'), 'r'))
        self.start_time = start_time
        relay_setup(self.cfg['relay_channel'])
        self.ccs811 = CCS811()
        tca9548a.change_multiplexer_channel(0x70, 0)
        self.chip_id, self.chip_version = read_chip_id()

    def _print_debugging_info(self, temperature, pressure, humidity, tvoc, eco2):

        msg_header = "\n=============================================\n"
        msg_body = ""

        print_msg = '| {:<11} | {:>23} {:<3} |\n'
        time_now = str(datetime.now())[:23]

        status_data = {"Chip ID": {'value': self.chip_id, 'measurement_unit': ''},
                       "Version": {'value': self.chip_version, 'measurement_unit': ''},
                       "Temperature": {'value': temperature, 'measurement_unit': '°C'},
                       "Pressure": {'value': pressure, 'measurement_unit': 'hPa'},
                       "Humidity": {'value': humidity, 'measurement_unit': '%'},
                       "eCO2": {'value': eco2, 'measurement_unit': 'ppm'},
                       "TVOC": {'value': tvoc, 'measurement_unit': 'ppb'},
                       "Date": {"value": time_now, 'measurement_unit': ''}}

        for metric_stat, metric_data in status_data.items():
            if not msg_body:
                msg_body = msg_header + msg_body
            msg_body += print_msg.format(metric_stat, *metric_data.values())
        msg_footer = "=============================================\n"
        msg_body += msg_footer
        LOGGER.info(msg_body)

    @staticmethod
    def get_thermostat_data():
        tca9548a.change_multiplexer_channel(0x70, 0)
        temperature, pressure, humidity = read_all_values()

        return {'temperature': temperature, 'pressure': pressure, 'humidity': humidity}

    def get_air_quality_data(self):
        # thermostat_data = self.get_thermostat_data()
        tca9548a.change_multiplexer_channel(0x70, 1)
        self.ccs811.read_data()

        air_quality_data = {'tvoc': self.ccs811.get_tvoc(),
                            'eco2': self.ccs811.get_eco2(),
                            'status': self.ccs811.get_status(),
                            'raw_data': self.ccs811.get_raw_data(),
                            'error_id': self.ccs811.get_error_id()}

        return air_quality_data

    def run(self):
        air_data = self.get_air_quality_data()
        temp_data = self.get_thermostat_data()
        tolerance = self.schedule['all_week']['interval'][0]['general_temp']['tolerance']
        min_temp = self.schedule['all_week']['interval'][0]['general_temp']['min']
        max_temp = self.schedule['all_week']['interval'][0]['general_temp']['max']
        if temp_data['temperature'] < min_temp or temp_data['temperature'] < min_temp + tolerance:
            if not get_relay_state(self.cfg['relay_channel']):
                relay_on(self.cfg['relay_channel'])
                LOGGER.info(self.status_msg.format('ON',
                                                   datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                                                   temp_data['temperature'],
                                                   temp_data['humidity']))
        elif min_temp < temp_data['temperature'] <= max_temp or temp_data['temperature'] > max_temp:
            if get_relay_state(self.cfg['relay_channel']):
                relay_off(self.cfg['relay_channel'])
                LOGGER.info(self.status_msg.format('OFF',
                                                   datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                                                   temp_data['temperature'],
                                                   temp_data['humidity']))

        exit(0)
