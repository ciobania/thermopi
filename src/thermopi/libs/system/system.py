#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# author: 'ACIOBANI'
import subprocess


def get_pi_temp():
    """
    Return Pi CPU temperature.
    :return: formatted float temperature, with degree sign in Celsius
    :rtype: string
    """
    try:
        temp_cmd = '/usr/bin/vcgencmd measure_temp'
        result = subprocess.check_output(temp_cmd,
                                         shell=True,
                                         stderr=subprocess.STDOUT,
                                         universal_newlines=True)
        pi_temp = result.strip().replace('\'', chr(176))[5:]
    except subprocess.CalledProcessError as _:
        pi_temp = f"19.85{chr(176)}C"
    return pi_temp
