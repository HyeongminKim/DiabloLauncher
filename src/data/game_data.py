#-*- coding:utf-8 -*-

from os import environ, path, mkdir, remove
from src.utility.logcat import errorLevel, logformat

userApp = environ.get('AppData')
ignoreTime = 5

def FormatTime(milliseconds: float, rawType: bool):
    seconds_per_minute = 60
    seconds_per_hour   = 60  * seconds_per_minute
    seconds_per_day    = 24  * seconds_per_hour
    seconds_per_week   = 7   * seconds_per_day
    seconds_per_month  = 30  * seconds_per_day
    seconds_per_year   = 365 * seconds_per_day

    elapsed_time = milliseconds
    units = [ '년', '월', '주', '일', '시간', '분', '초' ]
    unit_per_hours = [ seconds_per_year, seconds_per_month, seconds_per_week, seconds_per_day, seconds_per_hour, seconds_per_minute, 1]
    ymwdhms = [ 0, 0, 0, 0, 0, 0, 0 ]

    for i, unit in enumerate(unit_per_hours):
        if rawType and i < 4:
            continue
        ymwdhms[i] = int(elapsed_time / unit)
        elapsed_time = elapsed_time - ymwdhms[i] * unit

    text = ''
    for i, unit in enumerate(units):
        if not rawType and ymwdhms[i] > 0:
            text = f'{text} {ymwdhms[i]}{unit}' if text != '' else f'{ymwdhms[i]}{unit}'

    if rawType:
        hour = ymwdhms[4]
        minute = ymwdhms[5]
        seconds = ymwdhms[6]
        logformat(errorLevel.INFO, f'The provided {milliseconds} milliseconds converted to rawType time - {hour}:{minute}.{seconds}.')
        return hour, minute, seconds
    else:
        logformat(errorLevel.INFO, f'The provided {milliseconds} milliseconds converted to readable time - {text}.')
        return text

def SaveGameRunningTime(playTime: float):
    runtimeFile = None
    try:
        if not path.isfile(f'{userApp}/DiabloLauncher/runtime.log'):
            if not path.isdir(f'{userApp}/DiabloLauncher'):
                logformat(errorLevel.INFO, 'DiabloLauncher directory does not exist. creating directory')
                mkdir(f'{userApp}/DiabloLauncher')
            logformat(errorLevel.INFO, 'runtime.log file does not exist. creating target file with write mode')
            runtimeFile = open(f'{userApp}/DiabloLauncher/runtime.log', 'w', encoding='utf-8')
        else:
            logformat(errorLevel.INFO, 'runtime.log file already exist. opening target file with append mode')
            runtimeFile = open(f'{userApp}/DiabloLauncher/runtime.log', 'a', encoding='utf-8')
        logformat(errorLevel.INFO, f'playTime: {playTime} will be write in {userApp}/DiabloLauncher/runtime.log')
        hours, minutes, seconds = FormatTime(playTime, True)
        if hours == 0 and minutes < ignoreTime:
            logformat(errorLevel.INFO, f'{playTime} will be ignored. The provided {hours}:{minutes}.{seconds} playtime lower then {ignoreTime} minutes.')
        else:
            runtimeFile.write(f'{str(playTime)}\n')
            logformat(errorLevel.INFO, f'Successfully wrote {playTime} in {userApp}/DiabloLauncher/runtime.log')
    except (OSError, FileExistsError) as error:
        logformat(errorLevel.ERR, f'Failed to save Game-play logs: {error}')
    finally:
        if runtimeFile is not None:
            runtimeFile.close()

def ClearGameRunningTime():
    if path.isfile(f'{userApp}/DiabloLauncher/runtime.log'):
        remove(f'{userApp}/DiabloLauncher/runtime.log')
    else:
        logformat(errorLevel.ERR, f'Failed to remove {userApp}/DiabloLauncher/runtime.log file. no such file or directory.')

