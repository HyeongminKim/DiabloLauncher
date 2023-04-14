#-*- coding:utf-8 -*-

from subprocess import check_output, CalledProcessError
from src.utility.logcat import logformat, errorLevel

def check_terminal_output(command: str, suppress: bool = False):
    try:
        return check_output(f'{command} 2> NUL', shell=True, encoding='utf-8').strip()
    except CalledProcessError:
        if not suppress: logformat(errorLevel.ERR, f'{command} returned non-zero exit status.')
        return None
