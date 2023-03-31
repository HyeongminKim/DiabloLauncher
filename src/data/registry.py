#-*- coding:utf-8 -*-

import winreg as reg
from os import path
from os import startfile
from src.utility.logcat import logformat, errorLevel

def ReturnRegistryQuery(regAddress: str, queryName: str = 'InstallLocation'):
    try:
        key = reg.HKEY_LOCAL_MACHINE
        with reg.OpenKey(key, regAddress, 0, reg.KEY_READ) as target:
            value, type = reg.QueryValueEx(target, queryName)

        if path.isfile(value) or path.isdir(value):
            logformat(errorLevel.INFO, f'{value} is exist in system.')
            return value
        else:
            raise FileNotFoundError
    except (OSError, WindowsError, FileNotFoundError):
        logformat(errorLevel.ERR, f'Unable to locate {regAddress} registry.')
        return None

def OpenProgramUsingRegistry(regAddress: str, queryName: str = 'DisplayIcon'):
    try:
        key = reg.HKEY_LOCAL_MACHINE
        with reg.OpenKey(key, regAddress, 0, reg.KEY_READ) as target:
            value, type = reg.QueryValueEx(target, queryName)

        if path.isfile(value) or path.isdir(value):
            logformat(errorLevel.INFO, f'{value} is exist in system.')
            startfile(value)
        else:
            logformat(errorLevel.ERR, 'Unable to launch target file or directory: no such file or directory.')
    except (OSError, WindowsError):
        logformat(errorLevel.ERR, f'Unable to locate {regAddress} registry.')

def TestRegistryValueAsFile(regAddress: str, queryName: str = 'DisplayIcon'):
    try:
        key = reg.HKEY_LOCAL_MACHINE
        with reg.OpenKey(key, regAddress, 0, reg.KEY_READ) as target:
            value, type = reg.QueryValueEx(target, queryName)

        if path.isfile(value) or path.isdir(value):
            logformat(errorLevel.INFO, f'{value} is exist in system.')
            return True
        else:
            raise FileNotFoundError
    except (OSError, WindowsError, FileNotFoundError):
        logformat(errorLevel.ERR, f'Unable to locate {regAddress} registry.')
        return False

def TestRegistryValueAsRaw(regAddress: str, queryName: str):
    try:
        key = reg.HKEY_CURRENT_USER
        with reg.OpenKey(key, regAddress, 0, reg.KEY_READ) as target:
            value, type = reg.QueryValueEx(target, queryName)

        if value == 0:
            logformat(errorLevel.INFO, f'{value} is exist in system.')
            return True
        else:
            raise OSError
    except (OSError, WindowsError):
        logformat(errorLevel.ERR, f'Unable to locate {regAddress} registry.')
        return False

