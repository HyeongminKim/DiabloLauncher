#-*- coding:utf-8 -*-

from os import environ
from subprocess import call
from datetime import datetime
from enum import Enum

call('', shell=True)
logLevel = environ.get('LOG_VERBOSE_LEVEL')

TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

class color(Enum):
    RESET = '\033[0m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    GRAY = '\033[90m'

class errorLevel(Enum):
    INFO = 0
    WARN = 1
    ERR = 2
    FATL = 3

def logformat(level: errorLevel, text: str):
    if level == errorLevel.INFO:
        if logLevel is not None and logLevel == "verbose":
            print(f"{color.GRAY.value}[INFO: {datetime.now().strftime(TIMESTAMP_FORMAT)}] {text}{color.RESET.value}")
    elif level == errorLevel.WARN:
        print(f"{color.YELLOW.value}[WARN: {datetime.now().strftime(TIMESTAMP_FORMAT)}] {text}{color.RESET.value}")
    elif level == errorLevel.ERR:
        print(f"{color.RED.value}[ ERR: {datetime.now().strftime(TIMESTAMP_FORMAT)}] {text}{color.RESET.value}")
    elif level == errorLevel.FATL:
        print(f"{color.MAGENTA.value}[FATL: {datetime.now().strftime(TIMESTAMP_FORMAT)}] {text}{color.RESET.value}")
        exit(1)
