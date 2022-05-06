#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# author: 'ACIOBANI'
import subprocess
from socket import gethostname, gethostbyname


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


def get_ip_and_hostname():
    """
    Get the host system IP address and hostname.
    :return: IP address and hostname
    :rtype: dict
    """
    host_name = gethostname()
    ip_address = gethostbyname(host_name)

    return {'host_name': host_name,
            'ip_address': ip_address}