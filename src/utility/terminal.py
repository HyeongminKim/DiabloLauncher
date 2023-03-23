#-*- coding:utf-8 -*-

import subprocess
from src.utility.logcat import logformat, errorLevel

def check_terminal_output(command: str):
    try:
        return subprocess.check_output(f'{command} 2> NUL', shell=True, encoding='utf-8').strip()
    except subprocess.CalledProcessError:
        logformat(errorLevel.ERR, f'{command} returned non-zero exit status.')
        return None
