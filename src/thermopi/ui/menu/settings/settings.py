from datetime import timedelta
from time import monotonic

from thermopi.libs.system.system import get_ip_and_hostname, get_pi_temp

BLACK = (0, 0, 0)


def settings(win):
    print('settings')
    HOST_NETWORK = get_ip_and_hostname()

    win.draw_text(f"HOSTNAME: {HOST_NETWORK['host_name']}", BLACK, 80, 100, 20)
    win.draw_text(f"IP: {HOST_NETWORK['ip_address']}", BLACK, 60, 130, 20)
    win.draw_text(f"UPTIME: {timedelta(seconds=monotonic())}", BLACK, 60, 160, 20)
    win.draw_text(f"TEMP: {get_pi_temp()}", BLACK, 60, 180, 20)
