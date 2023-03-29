#-*- coding:utf-8 -*-

from os import environ
from json import load, dump
from src.utility.logcat import logformat, errorLevel

userAppData = environ.get('AppData')

def loadConfigurationFile():
    try:
        with open(f'{userAppData}/Battle.net/Battle.net.config', 'r', encoding='utf-8') as file:
            data = load(file)

        target = data['Games']['osi']['AdditionalLaunchArguments']
        logformat(errorLevel.INFO, f'Current configured external command is "{target}".')
        return target
    except (FileNotFoundError, KeyError):
        logformat(errorLevel.WARN, 'external command does not configured yet.')
        return None

def dumpConfigurationFile(external_cmd: str):
    try:
        with open(f'{userAppData}/Battle.net/Battle.net.config', 'r', encoding='utf-8') as file:
            data = load(file)

        data['Games']['osi']['AdditionalLaunchArguments'] = external_cmd
        logformat(errorLevel.INFO, f'Altered configured external command: "{external_cmd}".')

        with open(f'{userAppData}/Battle.net/Battle.net.config', 'w', encoding='utf-8') as file:
            dump(data, file, indent='    ')

        return True
    except (FileNotFoundError, KeyError):
        logformat(errorLevel.WARN, 'external command does not configured yet.')
        return False
