import logging
import os
import sys

from datetime import datetime

from twisted.logger import Logger

MODULE_PATH = os.path.dirname(__file__)

CFG_DIR = os.path.join(MODULE_PATH, 'configs')
LIBS_DIR = os.path.join(MODULE_PATH, 'libs')
IMAGES_DIR = os.path.join(MODULE_PATH, 'images')
FONTS_DIR = os.path.join(MODULE_PATH, 'fonts')
print('MODULE_PATH: ', MODULE_PATH)
print('CFG_DIR: ', CFG_DIR)
print('LIBS_DIR: ', LIBS_DIR)
print('IMAGES_DIR: ', IMAGES_DIR)
print('FONTS_DIR: ', FONTS_DIR)

sys.path.append(os.path.abspath(os.path.join(MODULE_PATH, os.pardir)))

SH_LOG_LEVEL = os.getenv('SH_LOG_LEVEL', 'INFO')
FH_LOG_LEVEL = os.getenv('FH_LOG_LEVEL', 'DEBUG')

DT_TIMETUPLE = datetime.now().timetuple()[:6]
TSTMP_PTTRN = '%Y-%m-%d %H:%M:%S'

LOG_TIMESTAMP = '_'.join(map(str, DT_TIMETUPLE))
LOGS_PATH = '{}/logs/'.format(MODULE_PATH)

if not os.path.exists(LOGS_PATH):
    os.makedirs(LOGS_PATH)

LOG_FILE_NAME = '{}{}.log'.format(LOGS_PATH, LOG_TIMESTAMP)

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(getattr(logging, FH_LOG_LEVEL))

FH = logging.FileHandler(LOG_FILE_NAME)
FH.setLevel(getattr(logging, FH_LOG_LEVEL))

SH = logging.StreamHandler()
SH.setLevel(getattr(logging, SH_LOG_LEVEL))

# create formatter and add it to the handlers
FORMATTER_PTTRN = '%(asctime)s - %(name)s.%(module)s.%(funcName)s - %(levelname)s - %(message)s'
LOG_FORMATTER = logging.Formatter(FORMATTER_PTTRN)
FH.setFormatter(LOG_FORMATTER)
SH.setFormatter(LOG_FORMATTER)

LOGGER.addHandler(FH)
LOGGER.addHandler(SH)

LOG = Logger(namespace="thermopi_ns")
