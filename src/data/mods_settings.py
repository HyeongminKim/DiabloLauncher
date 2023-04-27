#-*- coding:utf-8 -*-

from os import environ
from json import load, dump, JSONDecodeError
from src.utility.logcat import logformat, errorLevel

userAppData = environ.get('AppData')

def loadConfigurationFile():
    try:
        with open(f'{userAppData}/Battle.net/Battle.net.config', 'r', encoding='utf-8') as file:
            data = load(file)

        target = data['Games']['osi']['AdditionalLaunchArguments']
        logformat(errorLevel.INFO, f'Current configured external command is "{target}".')
        return target
    except (JSONDecodeError):
        logformat(errorLevel.FATL, "Unable to load configure file. reason: contains illegal JSON structures type or syntax.")
        return None
    except (FileNotFoundError, KeyError):
        logformat(errorLevel.WARN, 'external command does not configured yet.')
        return None

def dumpConfigurationFile(external_cmd: str):
    try:
        with open(f'{userAppData}/Battle.net/Battle.net.config', 'r', encoding='utf-8') as file:
            data = load(file)

        checkConfigurationStructure()
        data['Games']['osi']['AdditionalLaunchArguments'] = external_cmd
        logformat(errorLevel.INFO, f'Altered configured external command: "{external_cmd}".')
        with open(f'{userAppData}/Battle.net/Battle.net.config', 'w', encoding='utf-8') as file:
            dump(data, file, indent=4)
        return True
    except (FileNotFoundError, KeyError):
        logformat(errorLevel.WARN, 'external command does not configured yet.')
        return False

def checkConfigurationStructure():
    try:
        with open(f'{userAppData}/Battle.net/Battle.net.config', 'r', encoding='utf-8') as file:
            data = load(file)

        target = data['Games']['osi']['AdditionalLaunchArguments']
        logformat(errorLevel.INFO, f'Tested configured external command: "{target}".')
    except KeyError:
        logformat(errorLevel.INFO, 'external command does not configured yet. Making configuration structures.')
        data['Games']['osi']['AdditionalLaunchArguments'] = ''
        with open(f'{userAppData}/Battle.net/Battle.net.config', 'w', encoding='utf-8') as file:
            dump(data, file, indent=4)
    except (JSONDecodeError):
        logformat(errorLevel.FATL, "Unable to load configure file. reason: contains illegal JSON structures type or syntax.")
        return None
    except FileNotFoundError:
        logformat(errorLevel.WARN, 'external command does not configured yet.')
