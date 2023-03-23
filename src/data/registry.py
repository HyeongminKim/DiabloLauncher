#-*- coding:utf-8 -*-

import winreg as reg
from os import path
from os import startfile
from src.utility.logcat import logformat, errorLevel

def ReturnRegistryQuery(regAddress: str, queryName: str = 'InstallLocation'):
    target = None
    try:
        key = reg.HKEY_LOCAL_MACHINE
        target = reg.OpenKey(key, regAddress, 0, reg.KEY_READ)
        value, type = reg.QueryValueEx(target, queryName)
        if path.isfile(value) or path.isdir(value):
            logformat(errorLevel.INFO, f'{value} is exist in system.')
            if(target is not None): reg.CloseKey(target)
            return value
        else:
            raise FileNotFoundError
    except (OSError, WindowsError, FileNotFoundError):
        logformat(errorLevel.ERR, f'Unable to locate {regAddress} registry.')
        if(target is not None): reg.CloseKey(target)
        return None

def OpenProgramUsingRegistry(regAddress: str, queryName: str = 'DisplayIcon'):
    target = None
    try:
        key = reg.HKEY_LOCAL_MACHINE
        target = reg.OpenKey(key, regAddress, 0, reg.KEY_READ)
        value, type = reg.QueryValueEx(target, queryName)
        if path.isfile(value) or path.isdir(value):
            logformat(errorLevel.INFO, f'{value} is exist in system.')
            startfile(value)
        else:
            logformat(errorLevel.ERR, 'Unable to launch target file or directory: no such file or directory.')
    except (OSError, WindowsError):
        logformat(errorLevel.ERR, f'Unable to locate {regAddress} registry.')
    finally:
        if(target is not None): reg.CloseKey(target)

def TestRegistryValue(regAddress: str, queryName: str = 'DisplayIcon'):
    target = None
    try:
        key = reg.HKEY_LOCAL_MACHINE
        target = reg.OpenKey(key, regAddress, 0, reg.KEY_READ)
        value, type = reg.QueryValueEx(target, queryName)
        if path.isfile(value) or path.isdir(value):
            logformat(errorLevel.INFO, f'{value} is exist in system.')
            if(target is not None): reg.CloseKey(target)
            return True
        else:
            raise FileNotFoundError
    except (OSError, WindowsError, FileNotFoundError):
        logformat(errorLevel.ERR, f'Unable to locate {regAddress} registry.')
        if(target is not None): reg.CloseKey(target)
        return False

