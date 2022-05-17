#!/usr/bin/env python
import math
try:
    import pigpio
except ModuleNotFoundError as _:
    print('Running locally...')

from thermopi.libs.ccs811.ccs811_param import *


class CCS811:
    def __init__(self, bus_port=1, addr=0x5a, mode=CCS811_MODE_60SEC):

        # Check that mode is valid.
        if not (CCS811_MODE_IDLE <= mode <= CCS811_MODE_250MS):
            raise ValueError('Unexpected mode: {}'.format(mode))

        try:
            pigpio_bus = pigpio.pi()
            if not pigpio_bus.connected:
                print('Cannot open I2C bus.')

            self.bus = pigpio_bus
            self._h = pigpio_bus.i2c_open(bus_port, addr)
            self._raw_data = None
            self._status = 0
            self._meas_mode = 0
            self._error_id = 0
            self._TVOC = 0
            self._eCO2 = 0
            self.tempOffset = 0

            # check that the HW id is correct
            hw_id = self._read_reg(CCS811_HW_ID, 1)[0]
            if hw_id != CCS811_HW_ID_CODE:
                raise Exception("Device ID returned is not correct! Please check your wiring.")

            self.sw_reset()

            time.sleep(0.5)

            # try to start the app
            self._write([CCS811_BOOTLOADER_APP_START])
            time.sleep(0.2)

            # make sure there are no errors, and we have entered application mode
            if self._get_status() & ERROR_MASK:
                raise Exception(
                    "Device returned an Error! Try removing and reapplying power to the device and running the code again.")
            if not (self._status & FW_MODE_MASK):
                raise Exception("Device did not enter application mode! If you got here, \
                     there may be a problem with the firmware on your sensor.")

            # default to read every second
            self._meas_mode_DRIVE_MODE = 4
            self._meas_mode_INT_DATARDY = 0
            self._meas_mode_INT_THRESH = 0
            self._set_meas_mode()

            # self.enable_interrupt()
        except (Exception, ) as _:
            self._TVOC = 0
            self._eCO2 = 0
            self._raw_data = 0
            self._status = 0
            self._error_id = 0

    def cancel(self):
        """
        Cancel sensor readings.
        :return:
        :rtype:
        """
        self.bus.stop()

    def _read_reg(self, reg, data_bytes):
        self.bus.i2c_write_device(self._h, [reg])
        count, data = self.bus.i2c_read_device(self._h, data_bytes)
        return data

    def _write(self, data):
        self.bus.i2c_write_device(self._h, data)

    def _set_meas_mode(self):
        val = ((self._meas_mode_DRIVE_MODE << 4) |
               (self._meas_mode_INT_DATARDY << 3) |
               (self._meas_mode_INT_THRESH << 2))
        self._write([CCS811_MEAS_MODE, val])

    def set_drive_mode(self, mode):
        self._meas_mode_DRIVE_MODE = mode
        self._set_meas_mode()

    def enable_interrupt(self):
        self._meas_mode_INT_DATARDY = 1
        self._set_meas_mode()

    def disable_interrupt(self):
        self._meas_mode_INT_DATARDY = 0
        self._set_meas_mode()

    def data_ready(self):
        return self._get_status() & DATA_READY_MASK

    def read_data(self):
        try:
            buf = self._read_reg(CCS811_ALG_RESULT_DATA, 8)
            self._eCO2 = ((buf[0] & 0x7f) << 8) | buf[1]
            self._TVOC = ((buf[2] & 0x7f) << 8) | buf[3]
            self._status = buf[4]
            self._error_id = buf[5]
            self._raw_data = (buf[6] << 8) | buf[7]
            self._get_error_id()
        except (Exception, ) as _:
            self._eCO2 = 198
            self._TVOC = 31985
            self._status = 152
            self._error_id = 128
            self._raw_data = 41985

    # def set_environmental_data(self, humidity, temperature):
    #     """
    #     Humidity is stored as an unsigned 16 bits in 1/512%RH. The
    #     default value is 50% = 0x64, 0x00. As an example 48.5%
    #     humidity would be 0x61, 0x00.
    #
    #     Temperature is stored as an unsigned 16 bits integer in 1/512
    #     degrees there is an offset: 0 maps to -25C. The default value is
    #     25C = 0x64, 0x00. As an example 23.5% temperature would be
    #     0x61, 0x00.
    #     The internal algorithm uses these values (or default values if
    #     not set by the application) to compensate for changes in
    #     relative humidity and ambient temperature.
    #     """
    #
    #     hum_perc = humidity << 1
    #
    #     parts = math.fmod(temperature)
    #     fractional = parts[0]
    #     temperature = parts[1]
    #
    #     temp_high = ((temperature + 25) << 9)
    #     temp_low = ((fractional / 0.001953125) & 0x1FF)
    #
    #     temp_conv = (temp_high | temp_low)
    #
    #     self._write([CCS811_ENV_DATA,
    #                  hum_perc,
    #                  0x00,
    #                  ((temp_conv >> 8) & 0xFF),
    #                  (temp_conv & 0xFF)])

    # calculate temperature based on the NTC register
    def calculate_temperature(self):

        buf = self._read_reg(CCS811_NTC, 4)

        v_ref = (buf[0] << 8) | buf[1]
        vr_ntc = (buf[2] << 8) | buf[3]
        r_ntc = (float(vr_ntc) * float(CCS811_REF_RESISTOR) / float(v_ref))

        ntc_temp = math.log(r_ntc / 10000.0)
        ntc_temp /= 3380.0
        ntc_temp += 1.0 / (25 + 273.15)
        ntc_temp = 1.0 / ntc_temp
        ntc_temp -= 273.15
        return ntc_temp - self.tempOffset

    def set_thresholds(self, low_med, med_high, hysteresis):

        buf = [CCS811_THRESHOLDS,
               ((low_med >> 8) & 0xF),
               (low_med & 0xF),
               ((med_high >> 8) & 0xF),
               (med_high & 0xF),
               hysteresis
               ]

        self._write(buf)

    def sw_reset(self):
        self._write([CCS811_SW_RESET, 0x11, 0xE5, 0x72, 0x8A])

    def _get_error_id(self):
        self._error_id = self._read_reg(CCS811_ERROR_ID, 1)[0]

    def _get_status(self):
        self._status = self._read_reg(CCS811_STATUS, 1)[0]
        if self._status & ERROR_MASK:
            self._get_error_id()
        return self._status

    def get_error_id(self):
        return self._error_id

    def get_status(self):
        return self._status

    def get_tvoc(self):
        """
        Retrieve TVOC (Total Volatile Organic Compound)
        Concentration is between 0 and 1187 parts per billion (ppb)
        Can detect following compounds:
            - Alcohols
            - Aldehydes
            - Ketones
            - Organic Acids
            - Amines
            - Aliphatic and
            - Aromatic Hydrocarbons
        :return:
        :rtype:
        """
        return self._TVOC

    def get_eco2(self):
        """
        Retrieve eCO2 (equivalent calculated carbon-dioxide).
        Concentration is between 400 and 8192 parts per million (ppm)
        :return: eco2 value
        :rtype: int
        """
        return self._eCO2

    def get_raw_data(self):
        return self._raw_data


if __name__ == "__main__":

    import time

    s = CCS811()
    stop = time.time() + 10000000
    print("#  \tTVOC  \teCO2  \tstatus  \traw_data  \terror")

    n = 0
    while time.time() < stop:
        time.sleep(1)
        n += 1

        s.read_data()
        print("{}  \t{}  \t{}  \t{}  \t\t{}  \t\t{}".
              format(n, s.get_tvoc(), s.get_eco2(),
                     s.get_status(), s.get_raw_data(), s.get_error_id()))

    s.cancel()


# #       TVOC    eCO2    status          raw_data        error
# 1       0       400     152             7588            0
# 2       0       400     152             7603            0
