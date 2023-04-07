#-*- coding:utf-8 -*-

from os import environ, path, mkdir
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

def LoadGameRunningTime():
    data = []
    stat_max = 0
    stat_sum = 0
    try:
        if path.isfile(f'{userApp}/DiabloLauncher/runtime.log'):
            with open(f'{userApp}/DiabloLauncher/runtime.log', 'r', encoding='utf-8') as runtimeFile:
                logformat(errorLevel.INFO, f'Loading game stats {userApp}/DiabloLauncher/runtime.log with read only mode.')
                while True:
                    line = runtimeFile.readline()
                    if not line:
                        break
                    data.append(line)
                for index, line in enumerate(data, 1):
                    logformat(errorLevel.INFO, f"{'{:5d}'.format(index)} {float(line)}")
                    if stat_max < float(line):
                        stat_max = float(line)
                    stat_sum += float(line)
                logformat(errorLevel.INFO, 'Successfully Loaded game stats file.')

                if data is not None and stat_sum != 0:
                    return [len(data), stat_max, stat_sum, (stat_sum / len(data))]

                if data is not None and stat_sum == 0:
                    return [len(data), stat_max, 0, 0]

                return [0, 0, 0, 0]
        else:
            raise FileNotFoundError
    except (OSError, FileNotFoundError) as error:
        logformat(errorLevel.ERR, f'Failed to load Game-play logs: {error}')
        return [0, 0, 0, 0]

def SaveGameRunningTime(playTime: float):
    try:
        hours, minutes, seconds = FormatTime(playTime, True)
        if hours == 0 and minutes < ignoreTime:
            logformat(errorLevel.INFO, f'{playTime} will be ignored. The provided {hours}:{minutes}.{seconds} playtime lower then {ignoreTime} minutes.')
            return

        logformat(errorLevel.INFO, f'playTime: {playTime} will be write in {userApp}/DiabloLauncher/runtime.log')
        if not path.isfile(f'{userApp}/DiabloLauncher/runtime.log'):
            if not path.isdir(f'{userApp}/DiabloLauncher'):
                logformat(errorLevel.INFO, 'DiabloLauncher directory does not exist. creating directory')
                mkdir(f'{userApp}/DiabloLauncher')

            logformat(errorLevel.INFO, 'runtime.log file does not exist. creating target file with write mode')
            with open(f'{userApp}/DiabloLauncher/runtime.log', 'w', encoding='utf-8') as runtimeFile:
                runtimeFile.write(f'{str(playTime)}\n')
                logformat(errorLevel.INFO, f'Successfully wrote {playTime} in {userApp}/DiabloLauncher/runtime.log')
        else:
            logformat(errorLevel.INFO, 'runtime.log file already exist. opening target file with append mode')
            with open(f'{userApp}/DiabloLauncher/runtime.log', 'a', encoding='utf-8') as runtimeFile:
                runtimeFile.write(f'{str(playTime)}\n')
                logformat(errorLevel.INFO, f'Successfully wrote {playTime} in {userApp}/DiabloLauncher/runtime.log')

    except (OSError, FileExistsError) as error:
        logformat(errorLevel.ERR, f'Failed to save Game-play logs: {error}')

def ClearGameRunningTime():
    if path.isfile(f'{userApp}/DiabloLauncher/runtime.log'):
        with open(f'{userApp}/DiabloLauncher/runtime.log', 'w', encoding='utf-8'):
            logformat(errorLevel.INFO, f'Successfully flushed {userApp}/DiabloLauncher/runtime.log file.')
    else:
        logformat(errorLevel.ERR, f'Failed to remove {userApp}/DiabloLauncher/runtime.log file. no such file or directory.')

