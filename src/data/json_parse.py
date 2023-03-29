#-*- coding:utf-8 -*-

from os import environ
from json import load, dump
from src.utility.logcat import logformat, errorLevel

userAppData = environ.get('AppData')

def loadConfigurationFile():
    try:
        with open(f'{userAppData}\Battle.net\Battle.net.config', 'r') as file:
            data = load(file)
            target = data['Games']['osi']['AdditionalLaunchArguments']
            logformat(errorLevel.INFO, f'Current configured external command is "{target}".')
            return target
    except (FileNotFoundError, KeyError):
        logformat(errorLevel.WARN, 'external command does not configured yet.')
        return None
