#-*- coding:utf-8 -*-

# pylint: disable=W0603

from os import environ, path, mkdir
from enum import Enum
from json import load, dump, JSONDecodeError
from src.utility.logcat import logformat, errorLevel

class parentLocation(Enum):
    UserAppData = environ.get('AppData')
    UserLocalAppData = environ.get('LocalAppData')
    ProgramData = environ.get('ProgramData')

def loadSettings(scope: parentLocation, target_key: list[str]):
    try:
        makeConfigurationFileStructures(scope)
        with open(f'{scope.value}/DiabloLauncher/DiabloLauncher.config', 'r', encoding='utf-8') as file:
            data = load(file)

        checkConfigurationStructure(scope, target_key)

        if len(target_key) == 2:
            target = data[target_key[0]][target_key[1]]
        elif len(target_key) == 3:
            target = data[target_key[0]][target_key[1]][target_key[2]]

        logformat(errorLevel.INFO, f'Current configured {target_key} settings is "{target}".')
        return target
    except (JSONDecodeError):
        logformat(errorLevel.FATL, f"Unable to load {scope} settings. reason: contains illegal JSON structures type or syntax.")
        return None
    except (FileNotFoundError, KeyError):
        logformat(errorLevel.WARN, f'The current {target_key} settings does not configured yet.')
        return None

def dumpSettings(scope: parentLocation, target_key: list[str], target_value: any):
    try:
        makeConfigurationFileStructures(scope)
        with open(f'{scope.value}/DiabloLauncher/DiabloLauncher.config', 'r', encoding='utf-8') as file:
            data = load(file)

        checkConfigurationStructure(scope, target_key)

        if len(target_key) == 2:
            data[target_key[0]][target_key[1]] = target_value
        elif len(target_key) == 3:
            data[target_key[0]][target_key[1]][target_key[2]] = target_value

        logformat(errorLevel.INFO, f'Altered configured {target_key} settings: "{target_value}".')
        with open(f'{scope.value}/DiabloLauncher/DiabloLauncher.config', 'w', encoding='utf-8') as file:
            dump(data, file, indent=4)
        return True
    except (FileNotFoundError, KeyError):
        logformat(errorLevel.WARN, f'The current {target_key} settings does not configured yet.')
        return False

def makeConfigurationFileStructures(scope: parentLocation):
    if scope == parentLocation.UserAppData:
        config_init = {
            "General": {
                "AgentLaunched": False,
                "LastWindowPosition": [100, 100]
            }
        }
    elif scope == parentLocation.UserLocalAppData:
        config_init = {
            "General": {
                "LoggingInfoLevel": False,
                "TestSpeakerSoundPlay": False,
                "GameChannel": "Diablo",
                "GameStartCommand": None,
                "GameStopCommand": None
            },
            "ScreenResolution": {
                "IgnoreResProgramInstallDialog": False,
                "OriginResolutionVector": {
                    "OriginX": None,
                    "OriginY": None,
                    "OriginFR": None,
                },
                "AlteredResolutionVector": {
                    "AlteredX": None,
                    "AlteredY": None,
                    "AlteredFR": None,
                }
            },
            "ModsManager": {
                "IgnoreModsMergeDialog": False,
                "PreferMods": None
            }
        }
    elif scope == parentLocation.ProgramData:
        config_init = {
            "ScreenResolution": {
                "IgnoreResProgramInstallDialog": False,
                "OriginResolutionVector": {
                    "OriginX": None,
                    "OriginY": None,
                    "OriginFR": None,
                },
                "AlteredResolutionVector": {
                    "AlteredX": None,
                    "AlteredY": None,
                    "AlteredFR": None,
                }
            }
        }

    try:
        if not path.isfile(f'{scope.value}/DiabloLauncher/DiabloLauncher.config'):
            if not path.isdir(f'{scope.value}/DiabloLauncher'):
                mkdir(f'{scope.value}/DiabloLauncher')
            with open(f'{scope.value}/DiabloLauncher/DiabloLauncher.config', 'w', encoding='utf-8') as file:
                dump(config_init, file, indent=4)
            logformat(errorLevel.INFO, f'Successfullty Generated configured settings in {scope}.')
        else:
            logformat(errorLevel.INFO, f'configured settings already exist in {scope}.')
    except (JSONDecodeError):
        logformat(errorLevel.FATL, f"Unable to load {scope} settings. reason: contains illegal JSON structures type or syntax.")
        return None
    except (TypeError, FileExistsError, ValueError, RecursionError):
        logformat(errorLevel.ERR, f'Unable to Generated configured settings in {scope}. Internal Error!')


def checkConfigurationStructure(scope: parentLocation, target_key: list[str]):
    try:
        with open(f'{scope.value}/DiabloLauncher/DiabloLauncher.config', 'r', encoding='utf-8') as file:
            data = load(file)

        if len(target_key) == 2:
            target = data[target_key[0]][target_key[1]]
        elif len(target_key) == 3:
            target = data[target_key[0]][target_key[1]][target_key[2]]

        logformat(errorLevel.INFO, f'Tested configured {target_key} settings: "{target}".')
    except KeyError:
        logformat(errorLevel.WARN, f'The current {target_key} settings does not configured yet. Making configuration structures.')

        if len(target_key) == 2:
            data[target_key[0]][target_key[1]] = None
        elif len(target_key) == 3:
            data[target_key[0]][target_key[1]][target_key[2]] = None

        with open(f'{scope.value}/DiabloLauncher/DiabloLauncher.config', 'w', encoding='utf-8') as file:
            dump(data, file, indent=4)
    except (JSONDecodeError):
        logformat(errorLevel.FATL, f"Unable to load {scope} settings. reason: contains illegal JSON structures type or syntax.")
        return None
    except FileNotFoundError:
        logformat(errorLevel.WARN, f'The current {target_key} settings does not configured yet.')
