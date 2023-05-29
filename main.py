#-*- coding:utf-8 -*-

# pylint: disable=W0104,W0603,W0621
# pylint: disable=C0200,C0302,C0415,R1722,C0115,C0116

try:
    from subprocess import call, Popen
    call('', shell=True)
    f'[FATL: 70-01-01 12:00] The DiabloLauncher stopped due to unsupported python version. (version_info < {3.6})'

    import os
    from src.utility.logcat import logformat, errorLevel, color
    from src.utility.terminal import check_terminal_output
except (ModuleNotFoundError, ImportError) as error:
    print(f'\033[35m[FATL: 70-01-01 12:00] The DiabloLauncher stopped due to {error}\033[0m')
    exit(1)

userApp = os.environ.get('AppData')
userLocalApp = os.environ.get('LocalAppData')

try:
    import platform
    if platform.system() == 'Darwin':
        call(f"osascript -e 'display alert \"지원하지 않는 OS 감지됨\" message \"디아블로 런처는 현재 {platform.system()}을(를) 지원하지 않습니다. \" as critical' &> /dev/null", shell=True)
        raise OSError(f'{platform.system()} system does not support yet.')
    elif platform.system() == 'Linux':
        call(f"whiptail --msgbox --title '지원하지 않는 OS 감지됨' '디아블로 런처는 현재 {platform.system()}을(를) 지원하지 않습니다. ' 10 60 &> /dev/null", shell=True)
        raise OSError(f'{platform.system()} system does not support yet.')
    elif platform.system() != 'Windows':
        print(f'\033[33m[FATL: 70-01-01 12:00] This {platform.system()} system will not supported native GUI alert.\033[0m')
        raise OSError(f'{platform.system()} system does not support yet.')

    call('chcp 65001 > NUL', shell=True)
    logformat(errorLevel.INFO, 'Active code page: UTF-8 (0xfde9)')

    if platform.release() == '7' or platform.release() == '8' or platform.release() == '10' or platform.release() == '11':
        logformat(errorLevel.INFO, 'support OS detected.')
    else:
        logformat(errorLevel.FATL, f'{platform.system()} {platform.release()} does not support. Please check Diablo Requirements and Specifications.')

    import multiprocessing
    import sys
    from winsound import Beep
    import webbrowser
    from urllib import request, error as RequestError

    if multiprocessing.cpu_count() >= 2 and sys.maxsize > 2**32:
        logformat(errorLevel.INFO, f'supported {platform.processor()} CPU detected. creating GUI...')
    else:
        logformat(errorLevel.FATL, f"{platform.processor()} CPU does not support (core: {multiprocessing.cpu_count()}, {'x64' if sys.maxsize > 2**32 else 'x86'}).\n\tPlease check Diablo Requirements and Specifications.")

    import signal
    import logging

    from datetime import datetime
    import time

    from tkinter import Tk, Toplevel
    from tkinter import Label
    from tkinter import Button, Checkbutton
    from tkinter import (LEFT, RIGHT, BOTTOM)
    from tkinter import (W, CENTER)
    from tkinter import Menu, OptionMenu
    from tkinter import messagebox
    from tkinter import Entry
    from tkinter import Frame
    from tkinter import StringVar, IntVar

    from src.data.check_app_installed import ReturnRegistryQuery, OpenProgramUsingRegistry, TestRegistryValueAsFile, TestRegistryValueAsRaw
    from src.data.playtime_controller import FormatTime, SaveGameRunningTime, LoadGameRunningTime, ClearGameRunningTime, ignoreTime
    from src.data.mods_settings import loadConfigurationFile, dumpConfigurationFile
    from src.data.app_settings import loadSettings, dumpSettings, parentLocation
except (ModuleNotFoundError, ImportError, OSError) as error:
    print(f'\033[35m[FATL: 70-01-01 12:00] The DiabloLauncher stopped due to {error}\033[0m')
    exit(1)

diabloExecuted = False
updateChecked = False
forceReboot = False
releaseMode = False

rebootWaitTime = 10
loadWaitTime = 10

gameStartTime = None
gameEndTime = None

diablo2Path = None
diablo3Path = None
diablo4Path = None

definedMod = None
modsPreferPreviousSetting = None
modsInstalledList = None
modsPreferOptionMenu = None

resolutionProgram = False

originX = None
originY = None
originFR = None
alteredX = None
alteredY = None
alteredFR = None

testResOriginX = None
testResOriginY = None
testResOriginFR = None
testResAlteredX = None
testResAlteredY = None
testResAlteredFR = None

modsMuteSettings = False
verboseSettings = False
resIgnoreAlert = False

root = None
launch = None

welcome = None
switchButton = None
emergencyButton = None
status = None
statusbar = None
info = None
notice = None

applyHelp = None

fileMenu = None
toolsMenu = None
aboutMenu = None
modMenu = None
gameMenu = None

def ShowWindow():
    launch.geometry(f"300x125+{int(root.winfo_x() + root.winfo_reqwidth() / 2 - 300 / 2)}+{int(root.winfo_y() + root.winfo_reqheight() / 2 - 125 / 2)}")
    launch.deiconify()
    launch.after(1, launch.focus_force())
    launch.attributes('-topmost', 'true')

def HideWindow():
    root.after(1, root.focus_force())
    for widget in launch.winfo_children():
        logformat(errorLevel.INFO, f'abandoning module {widget}')
        widget.destroy()
    launch.title('무제')
    launch.withdraw()
    launch.attributes('-topmost', 'false')

def CheckResProgram():
    global resolutionProgram
    logformat(errorLevel.INFO, 'QRes install check')
    toolsMenu.entryconfig(3, state='normal')
    if os.path.isfile('C:/Windows/System32/Qres.exe') or os.path.isfile(f'{userLocalApp}/Programs/Common/QRes.exe'):
        if os.path.isfile(f'{userLocalApp}/Programs/Common/QRes.exe') and call('where QRes > NUL 2>&1', shell=True) != 0:
            logformat(errorLevel.ERR, f"QRes installed in {userLocalApp}/Programs/Common/QRes.exe. However that program will not discovered in future operation. Please add environment variable to fix this issue.")
            resolutionProgram = False
        else:
            logformat(errorLevel.INFO, f"QRes installed in {check_terminal_output('where QRes')}")
            resolutionProgram = True
    else:
        logformat(errorLevel.INFO, 'QRes did not installed')
        resolutionProgram = False

def CheckDarkMode():
    # dark bg="#272727"
    # dark menu bar bg="#202020"
    # dark txt color="#FFFFFF"
    # light bg="#F0F0F0"
    # light menu bar bg="#FFFFFF"
    # light txt color="#000000"
    if(TestRegistryValueAsRaw(r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize', 'AppsUseLightTheme')):
        root.configure(bg='#272727')
        launch.configure(bg='#272727')

        welcome['background'] = '#272727'
        status['background'] = '#272727'
        statusbar['background'] = '#272727'
        switchButton['background'] = '#272727'
        switchButton['activebackground'] = '#272727'
        emergencyButton['background'] = '#272727'
        emergencyButton['activebackground'] = '#272727'
        info['background'] = '#272727'
        notice['background'] = '#272727'

        welcome['foreground'] = '#FFFFFF'
        status['foreground'] = '#FFFFFF'
        statusbar['foreground'] = '#FFFFFF'
        switchButton['foreground'] = '#FFFFFF'
        switchButton['activeforeground'] = '#FFFFFF'
        emergencyButton['foreground'] = '#FFFFFF'
        emergencyButton['activeforeground'] = '#FFFFFF'
        info['foreground'] = '#FFFFFF'
        notice['foreground'] = '#FFFFFF'

        return True
    else:
        root.configure(bg='#F0F0F0')
        launch.configure(bg='#F0F0F0')

        welcome['background'] = '#F0F0F0'
        status['background'] = '#F0F0F0'
        statusbar['background'] = '#F0F0F0'
        switchButton['background'] = '#F0F0F0'
        switchButton['activebackground'] = '#F0F0F0'
        emergencyButton['background'] = '#F0F0F0'
        emergencyButton['activebackground'] = '#F0F0F0'
        info['background'] = '#F0F0F0'
        notice['background'] = '#F0F0F0'

        welcome['foreground'] = '#000000'
        status['foreground'] = '#000000'
        statusbar['foreground'] = '#000000'
        switchButton['foreground'] = '#000000'
        switchButton['activeforeground'] = '#000000'
        emergencyButton['foreground'] = '#000000'
        emergencyButton['activeforeground'] = '#000000'
        info['foreground'] = '#000000'
        notice['foreground'] = '#000000'

        return False

def AlertWindow():
    msg_box = messagebox.askquestion('디아블로 런처', f'현재 디스플레이 해상도가 {alteredX}x{alteredY} 로 조정되어 있습니다. 게임이 실행 중인 상태에서 해상도 설정을 복구할 경우 퍼포먼스에 영향을 미칠 수 있습니다. 그래도 해상도 설정을 복구하시겠습니까?', icon='question')
    if msg_box == 'yes':
        LaunchGameAgent()
        ExitProgram()
    else:
        messagebox.showwarning('디아블로 런처', '해상도가 조절된 상태에서는 런처를 종료할 수 없습니다. 먼저 해상도를 기본 설정으로 변경해 주시기 바랍니다.')

def ExitProgram(*args):
    if(launch is not None and root is not None):
        for widget in launch.winfo_children():
            logformat(errorLevel.INFO, f'Shutting down and abandoning module {widget}')
            widget.destroy()
        launch.destroy()

        for widget in root.winfo_children():
            logformat(errorLevel.INFO, f'Shutting down and abandoning module {widget}')
            widget.destroy()
        dumpSettings(parentLocation.UserAppData, ["General", "LastWindowPosition"], [root.winfo_x(), root.winfo_y()])
        dumpSettings(parentLocation.UserAppData, ["General", "AgentLaunched"], False)
        root.destroy()
    exit(0)

def InterruptProgram(sig, frame):
    logformat(errorLevel.ERR, f'Keyboard Interrupt: {sig}')
    if diabloExecuted:
        LaunchGameAgent()
    ExitProgram()

def UpdateProgram():
    global updateChecked

    if releaseMode:
        logformat(errorLevel.INFO, 'Portable DiabloLauncher release does not supported auto-update function yet. Please wait until loading releases page.')
        webbrowser.open('https://github.com/HyeongminKim/DiabloLauncher/releases')
        messagebox.showwarning('디아블로 런처', 'EXE 파일로 배포된 디아블로 런처는 자동 업데이트를 아직 지원하지 않습니다. 최신 버전은 브라우저에서 확인해 주세요.')
        return

    if call('where git > NUL 2>&1', shell=True) == 0:
        localCommit = os.popen('git rev-parse HEAD').read().strip()
        localVersion = os.popen('git rev-parse --short HEAD').read().strip()
        cnt_branch = os.popen('git branch --show-current').read().strip()
        logformat(errorLevel.INFO, 'Checking program updates...')
        if call(f'git pull --rebase origin {cnt_branch} > NUL 2>&1', shell=True) == 0:
            updatedCommit = os.popen('git rev-parse HEAD').read().strip()
            remoteVersion = os.popen('git rev-parse --short HEAD').read().strip()
            result = check_terminal_output(f"git log --no-merges --pretty=format:'%s' {updatedCommit}...{localCommit}")

            if localVersion != remoteVersion:
                messagebox.showinfo('디아블로 런처', f"디아블로 런처가 성공적으로 업데이트 되었습니다.\n\n\t-- 새로운 기능 ({localVersion} → {remoteVersion}) --\n{result}\n\n업데이트를 반영하시려면 프로그램을 다시 시작해 주세요.")
                logformat(errorLevel.INFO, f'Successfully updated ({localVersion} → {remoteVersion}). Please restart DiabloLauncher to apply updates...')
            else:
                if updateChecked:
                    messagebox.showinfo('디아블로 런처', '디아블로 런처가 최신 버전입니다.')
                logformat(errorLevel.INFO, 'DiabloLauncher is Up to date.')
        elif call('ping -n 1 -w 1 www.google.com > NUL 2>&1', shell=True) != 0:
            messagebox.showwarning('디아블로 런처', '인터넷 연결이 오프라인인 상태에서는 디아블로 런처를 업데이트 할 수 없습니다. 나중에 다시 시도해 주세요.')
            logformat(errorLevel.ERR, 'Program update failed. Please check your internet connection.')
        else:
            Popen('git status', shell=True)
            messagebox.showwarning('디아블로 런처', '레포에 알 수 없는 오류가 발생하였습니다. 자세한 사항은 로그를 참조해 주세요. ')
            logformat(errorLevel.ERR, 'Program update failed. Please see the output.')
        updateChecked = True
    elif call('where git > NUL 2>&1', shell=True) != 0 and updateChecked:
        logformat(errorLevel.INFO, 'git command does not currently installed. downloading master.zip')
        webbrowser.open('https://github.com/HyeongminKim/DiabloLauncher/archive/refs/heads/master.zip')
        messagebox.showwarning('디아블로 런처', 'Git이 시스템에 설치되어 있지 않아 자동 업데이트를 사용할 수 없습니다. 다운로드 된 master.zip 파일 압축을 풀어 설치된 경로에 덮어쓰기해 주세요.')
    elif call('where git > NUL 2>&1', shell=True) != 0 and not updateChecked:
        logformat(errorLevel.WARN, 'Automatically checking for updates has been disabled. Run the updater function again to switch to legacy update mode. ')
        updateChecked = True

def GameLauncher(gameName: str, supportedX: int, supportedY: int, os_min: int):
    global diabloExecuted
    global gameStartTime

    result = check_terminal_output('tasklist | findstr "Battle.net.exe" > NUL 2>&1', True)
    if result is not None:
        logformat(errorLevel.ERR, "Unable to open Battle.net. reason: another Battle.net agent detected.")
        messagebox.showerror(title='디아블로 런처', message='Battle.net이 이미 실행 중 입니다. 디아블로를 안정적으로 플레이하기 위해 먼저 Battle.net을 종료해 주시기 바랍니다.')
        root.protocol("WM_DELETE_WINDOW", ExitProgram)
        HideWindow()
        UpdateStatusValue()
        ReloadStatusBar()
        return

    try:
        Beep(200, 500)
    except RuntimeError:
        logformat(errorLevel.ERR, 'No sound output device detected. Check your speaker connection.')
        messagebox.showerror(title='디아블로 런처', message='사운드 장치를 찾을 수 없습니다. 디아블로를 안정적으로 플레이하기 위해 먼저 스피커가 제대로 연결되어 있는지 확인해 주시기 바랍니다.')
        HideWindow()
        UpdateStatusValue()
        ReloadStatusBar()
        return

    diabloExecuted = True
    logformat(errorLevel.INFO, f'Launching {gameName}...')
    if resolutionProgram:
        if int(alteredX) < supportedX or int(alteredY) < supportedY:
            logformat(errorLevel.ERR, f'The {gameName} does not supported display resolution {alteredX}x{alteredY} {alteredFR}Hz')
            messagebox.showerror('디아블로 런처', f'{alteredX}x{alteredY} {alteredFR}Hz 해상도는 {gameName} 가 지원하지 않습니다. 자세한 사항은 공식 홈페이지를 확인하시기 바랍니다. ')
            diabloExecuted = False
            root.protocol("WM_DELETE_WINDOW", ExitProgram)
            HideWindow()
            UpdateStatusValue()
            ReloadStatusBar()
            return
        try:
            if int(platform.release()) >= os_min:
                logformat(errorLevel.INFO, f'The {gameName} supported current OS {platform.system()} {platform.release()}')
            else:
                raise ValueError
        except (ValueError, TypeError):
            logformat(errorLevel.ERR, f'The {gameName} does not supported current OS {platform.system()} {platform.release()}')
            messagebox.showerror('디아블로 런처', f'{platform.system()} {platform.release()} 은(는) {gameName} 가 지원하지 않습니다. 자세한 사항은 공식 홈페이지를 확인하시기 바랍니다. ')
            diabloExecuted = False
            root.protocol("WM_DELETE_WINDOW", ExitProgram)
            HideWindow()
            UpdateStatusValue()
            ReloadStatusBar()
            return
        if call(f'QRes /L | findstr /r "{alteredX}x" |findstr /r "{alteredY}," | findstr /r "\\<{alteredFR}\\>" > NUL 2>&1', shell=True) != 0:
            logformat(errorLevel.ERR, f'The current display does not supported choosed resolution {alteredX}x{alteredY} {alteredFR}Hz')
            messagebox.showwarning('디아블로 런처', f'{alteredX}x{alteredY} {alteredFR}Hz 해상도는 이 디스플레이에서 지원하지 않습니다. 시스템 환경 설정에서 지원하는 해상도를 확인하시기 바랍니다.')
            diabloExecuted = False
            root.protocol("WM_DELETE_WINDOW", ExitProgram)
            HideWindow()
            UpdateStatusValue()
            ReloadStatusBar()
            return

        Popen(f'QRes -X {alteredX} -Y {alteredY} -R {alteredFR} > NUL 2>&1', shell=True)
        switchButton['text'] = '디스플레이 해상도 복구\n(게임 종료시 사용)'
        root.protocol("WM_DELETE_WINDOW", AlertWindow)
        HideWindow()

        if(root.winfo_x() + root.winfo_reqwidth() > int(alteredX) or root.winfo_y() + root.winfo_reqheight() > int(alteredY)):
            root.geometry("520x360+100+100")
            logformat(errorLevel.WARN, 'Reset the window position to default due to the current resolution settings.')
    else:
        switchButton['text'] = '게임 종료'
        HideWindow()

    if(gameName == 'Diablo II Resurrected'):
        os.popen(f'"{diablo2Path}/{gameName} Launcher.exe"')
    elif(gameName == 'Diablo III'):
        os.popen(f'"{diablo3Path}/{gameName} Launcher.exe"')
    elif(gameName == 'Diablo IV'):
        os.popen(f'"{diablo4Path}/{gameName} Launcher.exe"')
    toolsMenu.entryconfig(3, state='disabled')
    gameStartTime = time.time()
    UpdateStatusValue()
    ReloadStatusBar()

def LaunchGameAgent():
    global diabloExecuted
    global gameEndTime
    if diabloExecuted:
        diabloExecuted = False
        logformat(errorLevel.INFO, 'Setting game mode is false...')
        root.protocol("WM_DELETE_WINDOW", ExitProgram)
        gameEndTime = time.time()
        switchButton['text'] = '디아블로 실행...'
        toolsMenu.entryconfig(3, state='normal')
        if resolutionProgram:
            if call(f'QRes /L | findstr /r "{originX}x" |findstr /r "{originY}," | findstr /r "\\<{originFR}\\>" > NUL 2>&1', shell=True) != 0:
                logformat(errorLevel.ERR, f'The current display does not supported choosed resolution {alteredX}x{alteredY} {alteredFR}Hz')
                messagebox.showwarning('디아블로 런처', f'{originX}x{originY} {originFR}Hz 해상도는 이 디스플레이에서 지원하지 않습니다. 시스템 환경 설정에서 지원하는 해상도를 확인하시기 바랍니다.')
            else:
                Popen(f'QRes -X {originX} -Y {originY} -R {originFR} > NUL 2>&1', shell=True)

        SaveGameRunningTime(gameEndTime - gameStartTime)
        hours, minutes, seconds = FormatTime(gameEndTime - gameStartTime, True)
        logformat(errorLevel.INFO, f'Running game time for this session: {hours}:{minutes}.{seconds}')
        if hours > 0:
            if minutes > 0 and seconds > 0:
                messagebox.showinfo('디아블로 런처', f'이번 세션에는 {hours}시간 {minutes}분 {seconds}초 동안 플레이 했습니다.')
            elif minutes > 0 and seconds == 0:
                messagebox.showinfo('디아블로 런처', f'이번 세션에는 {hours}시간 {minutes}분 동안 플레이 했습니다.')
            elif minutes == 0 and seconds > 0:
                messagebox.showinfo('디아블로 런처', f'이번 세션에는 {hours}시간 {seconds}초 동안 플레이 했습니다.')
            elif minutes == 0 and seconds == 0:
                messagebox.showinfo('디아블로 런처', f'이번 세션에는 {hours}시간 동안 플레이 했습니다. ')
        elif minutes >= ignoreTime:
            if seconds > 0:
                messagebox.showinfo('디아블로 런처', f'이번 세션에는 {minutes}분 {seconds}초 동안 플레이 했습니다. ')
            else:
                messagebox.showinfo('디아블로 런처', f'이번 세션에는 {minutes}분 동안 플레이 했습니다. ')
        UpdateStatusValue()
        ReloadStatusBar()
    else:
        launch.title('디아블로 버전 선택')

        note = Label(launch, text='사용가능한 디아블로 버전만 활성화 됩니다', height=2)
        diablo2 = Button(launch, text='Diablo II Resurrected\n설치되지 않음', width=20, height=5, command= lambda: GameLauncher('Diablo II Resurrected', 1280, 720, 10))
        diablo3 = Button(launch, text='Diablo III\n설치되지 않음', width=20, height=2, command= lambda: GameLauncher('Diablo III', 1024, 768, 7))
        diablo4 = Button(launch, text='Diablo IV EA\n설치되지 않음', width=20, height=2, command= lambda: GameLauncher('Diablo IV', 1280, 720, 10))
        # diablo4 = Button(launch, text='Diablo IV\n설치되지 않음', width=20, height=2, command= lambda: GameLauncher('Diablo IV', 1280, 720, 10))

        note.grid(row=0, column=0, columnspan=2)
        diablo2.grid(row=1, column=0, rowspan=2)
        diablo3.grid(row=1, column=1)
        diablo4.grid(row=2, column=1)

        if(CheckDarkMode()):
            note['background'] = '#272727'
            note['foreground'] = '#FFFFFF'
            diablo2['background'] = '#272727'
            diablo2['activebackground'] = '#272727'
            diablo2['foreground'] = '#FFFFFF'
            diablo2['activeforeground'] = '#FFFFFF'
            diablo3['background'] = '#272727'
            diablo3['activebackground'] = '#272727'
            diablo3['foreground'] = '#FFFFFF'
            diablo3['activeforeground'] = '#FFFFFF'
            diablo4['background'] = '#272727'
            diablo4['activebackground'] = '#272727'
            diablo4['foreground'] = '#FFFFFF'
            diablo4['activeforeground'] = '#FFFFFF'
        else:
            note['background'] = '#F0F0F0'
            note['foreground'] = '#000000'
            diablo2['background'] = '#F0F0F0'
            diablo2['activebackground'] = '#F0F0F0'
            diablo2['foreground'] = '#000000'
            diablo2['activeforeground'] = '#000000'
            diablo3['background'] = '#F0F0F0'
            diablo3['activebackground'] = '#F0F0F0'
            diablo3['foreground'] = '#000000'
            diablo3['activeforeground'] = '#000000'
            diablo4['background'] = '#F0F0F0'
            diablo4['activebackground'] = '#F0F0F0'
            diablo4['foreground'] = '#000000'
            diablo4['activeforeground'] = '#000000'

        if diablo2Path is None or not os.path.isfile(f'{diablo2Path}/Diablo II Resurrected Launcher.exe'):
            logformat(errorLevel.INFO, 'Diablo II Resurrected launch button disabled, because launcher is not detected.')
            diablo2['state'] = "disabled"
        else:
            logformat(errorLevel.INFO, 'Diablo II Resurrected launch button enabled.')
            diablo2['state'] = "normal"
            if os.path.isdir(f'{diablo2Path}/mods'):
                logformat(errorLevel.INFO, 'Diablo II Resurrected mods directory detected.')
                GetModDetails()
                envModState = loadSettings(parentLocation.UserLocalAppData, ["ModsManager", "IgnoreModsMergeDialog"])
                envMod = loadSettings(parentLocation.UserLocalAppData, ["ModsManager", "PreferMods"])
                if definedMod is not None and isinstance(definedMod, list) and (envModState is None or envModState is False) and envMod is None:
                    logformat(errorLevel.WARN, "Diablo II Resurrected mods are not cached. Because too many mods detected.")
                    diablo2['text'] = 'Diablo II Resurrected\n모드병합 필요'
                elif definedMod is not None and isinstance(definedMod, list) and envModState is not None and envModState is True:
                    logformat(errorLevel.INFO, "Diablo II Resurrected mods helper was disable due to IgnoreModsMergeDialog settings.")
                    diablo2['text'] = 'Diablo II Resurrected'
                elif definedMod is not None and isinstance(definedMod, str):
                    if os.path.isdir(f'{diablo2Path}/mods/{definedMod}/{definedMod}.mpq/data') or os.path.isfile(f'{diablo2Path}/mods/{definedMod}/{definedMod}.mpq'):
                        external_conf = loadConfigurationFile()
                        if external_conf is not None and external_conf == f' -mod {definedMod} -txt':
                            diablo2['text'] = f'Diablo II Resurrected\n{definedMod} 적용됨'
                        else:
                            diablo2['text'] = f'Diablo II Resurrected\n{definedMod} 감지됨'
                    else:
                        messagebox.showwarning(title='디아블로 모드 관리자', message='유효하지 않은 모드 배치가 감지되었습니다. ')
                        logformat(errorLevel.WARN, f"The mod {definedMod} does not followed by path:")
                        logformat(errorLevel.WARN, f"\t- {diablo2Path}/mods/{definedMod}/{definedMod}.mpq")
                        logformat(errorLevel.WARN, f"\t- {diablo2Path}/mods/{definedMod}/{definedMod}.mpq/data")
                        diablo2['text'] = 'Diablo II Resurrected'
                else:
                    logformat(errorLevel.INFO, "Diablo II Resurrected mods are not cached. Because mods was not installed yet.")
                    diablo2['text'] = 'Diablo II Resurrected'
            else:
                logformat(errorLevel.INFO, 'Diablo II Resurrected mods directory not found.')
                diablo2['text'] = 'Diablo II Resurrected'

        if diablo3Path is None or not os.path.isfile(f'{diablo3Path}/Diablo III Launcher.exe'):
            logformat(errorLevel.INFO, 'Diablo III launch button disabled, because launcher is not detected.')
            diablo3['state'] = "disabled"
        else:
            logformat(errorLevel.INFO, 'Diablo III launch button enabled.')
            diablo3['state'] = "normal"
            diablo3['text'] = 'Diablo III'

        if diablo4Path is None or not os.path.isfile(f'{diablo4Path}/Diablo IV Launcher.exe'):
            logformat(errorLevel.INFO, 'Diablo IV launch button disabled, because launcher is not detected.')
            diablo4['state'] = "disabled"
        else:
            logformat(errorLevel.INFO, 'Diablo IV launch button enabled.')
            diablo4['state'] = "normal"
            diablo4['text'] = 'Diablo IV EA'
            # diablo4['text'] = 'Diablo IV'

        diablo4['state'] = "disabled"
        diablo4['text'] = 'Diablo IV EA\n6월 2일 출시 예정'
        # diablo4['text'] = 'Diablo IV\n6월 6일 출시 예정'

        ShowWindow()
        launch.mainloop()

def BootAgent(poweroff: str):
    global forceReboot
    global gameEndTime
    forceReboot = True
    gameEndTime = time.time()
    if diabloExecuted:
        SaveGameRunningTime(gameEndTime - gameStartTime)
    if poweroff == 'r':
        emergencyButton['text'] = '긴급 재시동 준비중...\n(재시동 취소)'
        logformat(errorLevel.INFO, 'Starting Emergency reboot agent...')
    elif poweroff == 's':
        emergencyButton['text'] = '긴급 종료 준비중...\n(종료 취소)'
        logformat(errorLevel.INFO, 'Starting Emergency reboot agent...')
    if resolutionProgram:
        if call(f'QRes /L | findstr /r "{originX}x" |findstr /r "{originY}," | findstr /r "\\<{originFR}\\>" > NUL 2>&1', shell=True) != 0:
            logformat(errorLevel.ERR, f'The current display does not supported choosed resolution {alteredX}x{alteredY} {alteredFR}Hz')
            messagebox.showwarning('디아블로 런처', f'{originX}x{originY} {originFR}Hz 해상도는 이 디스플레이에서 지원하지 않습니다. 시스템 환경 설정에서 지원하는 해상도를 확인하시기 바랍니다.')
        else:
            Popen(f'QRes -X {originX} -Y {originY} -R {originFR} > NUL 2>&1', shell=True)
    HideWindow()
    UpdateStatusValue()
    if poweroff == 'r':
        Popen('shutdown -r -f -t 10 -c "Windows가 DiabloLauncher의 [긴급 재시동] 기능으로 인해 재시동 됩니다."', shell=True)
    elif poweroff == 's':
        Popen('shutdown -s -f -t 10 -c "Windows가 DiabloLauncher의 [긴급 종료] 기능으로 인해 종료 됩니다."', shell=True)
    logformat(errorLevel.INFO, 'Successfully executed Windows shutdown.exe')
    dumpSettings(parentLocation.UserAppData, ["General", "AgentLaunched"], False)
    statusbar['text'] = '로드할 수 없음'
    statusbar['anchor'] = W
    switchButton['state'] = "disabled"
    toolsMenu.entryconfig(3, state='disabled')

def EmgergencyReboot():
    global forceReboot
    if forceReboot:
        forceReboot = False
        emergencyButton['text'] = '긴급 전원 작업\n(게임 저장 후 실행 요망)'
        logformat(errorLevel.INFO, 'Aborting Emergency agent...')
        switchButton['state'] = "normal"
        toolsMenu.entryconfig(3, state='normal')
        Popen('shutdown -a', shell=True)
        logformat(errorLevel.INFO, 'Successfully executed Windows shutdown.exe')
        currentAgent = loadSettings(parentLocation.UserAppData, ["General", "AgentLaunched"])
        if currentAgent is not None and currentAgent is False:
            dumpSettings(parentLocation.UserAppData, ["General", "AgentLaunched"], True)
        else:
            msg_box = messagebox.askyesno(title='디아블로 런처', message='타 디아블로 런처가 다중 실행 잠금 설정을 수정하였으므로 해당 프로퍼티를 편집할 수 없습니다. 대신 이 디아블로 런처를 종료하시겠습니까?\n디아블로 런처를 종료하지 않을 경우 불안정해질 수 있습니다.', icon='warning')
            if msg_box:
                logformat(errorLevel.FATL, 'DiabloLauncher was killed. reason: User abort DiabloLauncher process.')
                exit(1)
        statusbar['anchor'] = CENTER
        UpdateStatusValue()
        ReloadStatusBar()
    else:
        launch.title('전원')
        if resolutionProgram and diabloExecuted:
            note = Label(launch, text=f'수행할 작업 시작전 {originX}x{originY} 해상도로 복구 후 계속')
        else:
            note = Label(launch, text='수행할 작업 선택')
        reboot = Button(launch, text='재시동', width=20, height=5, command= lambda: BootAgent('r'))
        halt = Button(launch, text='종료', width=20, height=5, command= lambda: BootAgent('s'))
        note.pack()
        reboot.pack(side=LEFT, padx=10)
        halt.pack(side=RIGHT, padx=10)

        if(CheckDarkMode()):
            note['background'] = '#272727'
            note['foreground'] = '#FFFFFF'
            reboot['background'] = '#272727'
            reboot['activebackground'] = '#272727'
            reboot['foreground'] = '#FFFFFF'
            reboot['activeforeground'] = '#FFFFFF'
            halt['background'] = '#272727'
            halt['activebackground'] = '#272727'
            halt['foreground'] = '#FFFFFF'
            halt['activeforeground'] = '#FFFFFF'
        else:
            note['background'] = '#F0F0F0'
            note['foreground'] = '#000000'
            reboot['background'] = '#F0F0F0'
            reboot['activebackground'] = '#F0F0F0'
            reboot['foreground'] = '#000000'
            reboot['activeforeground'] = '#000000'
            halt['background'] = '#F0F0F0'
            halt['activebackground'] = '#F0F0F0'
            halt['foreground'] = '#000000'
            halt['activeforeground'] = '#000000'

        ShowWindow()
        launch.mainloop()

def GetModDetails():
    global definedMod
    envValue = os.listdir(f'{diablo2Path}/mods')
    if isinstance(envValue, list) and len(envValue) > 1:
        logformat(errorLevel.INFO, f"Detected mods: {envValue}. checking PreferMods setting...")
        envMod = loadSettings(parentLocation.UserLocalAppData, ["ModsManager", "PreferMods"])
        if envMod is not None:
            for mod in envValue:
                logformat(errorLevel.INFO, f"checking mods.. listed: {mod}, preferMod: {envMod}")
                if mod == envMod:
                    logformat(errorLevel.INFO, f"Prefer mods: {mod}")
                    envValue = mod
                    break

            if isinstance(envValue, str):
                logformat(errorLevel.INFO, f"prefer mod was configured: {envValue}. the list of detected mods was overridden.")
                definedMod = envValue
            else:
                logformat(errorLevel.WARN, f"prefer mod is not configured. {envMod} does not exist in {diablo2Path}/mods. Diablo Launcher will mods partially.")
                definedMod = envValue
        else:
            logformat(errorLevel.WARN, "prefer mod is not configured. Diablo Launcher will mods partially.")
            definedMod = envValue
    elif isinstance(envValue, list) and len(envValue) == 1:
        logformat(errorLevel.INFO, f"Detected mod: {envValue}")
        definedMod = envValue[0]
    elif isinstance(envValue, list) and len(envValue) == 0:
        logformat(errorLevel.INFO, f"mods directory is currently exist but it is empty. Therefore GetModDetails function will handling {envValue} value to None")
        definedMod = None
    else:
        logformat(errorLevel.ERR, f"Requirements does not satisfied: The provided value {envValue} does not match list[str] type. Therefore GetModDetails function will handling {envValue} value to None")
        definedMod = None


def DownloadModsLink():
    webbrowser.open('https://www.google.com/search?q=Diablo+2+Resurrected+mod')

def SearchModInGitHub():
    webbrowser.open(f'https://github.com/search?q={definedMod}')

def ModsPreferSelector():
    msg_box = messagebox.askyesno(title='디아블로 모드', message='Diablo II Resurrected 모드를 병합하지 않고 선호하는 모드를 직접 선택 하시겠습니까?')
    if msg_box:
        SetLauncherConfigurationValues()

def FindGameInstalled():
    global diablo2Path
    global diablo3Path
    global diablo4Path
    global definedMod

    if(TestRegistryValueAsFile(r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Diablo II Resurrected')):
        logformat(errorLevel.INFO, 'Diablo II Resurrected mod check enabled.')
        gameMenu.entryconfig(0, state='normal')
        modMenu.entryconfig(3, state='normal')

        diablo2Path = ReturnRegistryQuery(r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Diablo II Resurrected')
        if os.path.isdir(f'{diablo2Path}/mods'):
            modMenu.entryconfig(0, state='normal')
            modMenu.entryconfig(1, label='활성화된 모드: 검색중...')
            modMenu.entryconfig(1, state='disabled')
            logformat(errorLevel.INFO, 'Diablo II Resurrected mods directory detected.')
            GetModDetails()
            envModState = loadSettings(parentLocation.UserLocalAppData, ["ModsManager", "IgnoreModsMergeDialog"])
            envMod = loadSettings(parentLocation.UserLocalAppData, ["ModsManager", "PreferMods"])

            if definedMod is not None and isinstance(definedMod, list) and (envModState is None or envModState is False) and envMod is None:
                logformat(errorLevel.WARN, "Diablo II Resurrected mods are not cached. Because too many mods detected.")
                modMenu.entryconfig(1, label=f'감지된 모드: {definedMod[0]} 외 {len(definedMod) - 1}개')
                modMenu.entryconfig(1, state='normal')
                modMenu.entryconfig(1, command=ModsPreferSelector)
            elif definedMod is not None and isinstance(definedMod, list) and envModState is not None and envModState is True:
                logformat(errorLevel.INFO, "Diablo II Resurrected mods helper was disable due to IgnoreModsMergeDialog settings.")
                modMenu.entryconfig(1, label='새로운 모드 탐색')
                modMenu.entryconfig(1, state='normal')
                modMenu.entryconfig(1, command=DownloadModsLink)
                definedMod = None
            elif definedMod is not None and isinstance(definedMod, str):
                if os.path.isdir(f'{diablo2Path}/mods/{definedMod}/{definedMod}.mpq/data') or os.path.isfile(f'{diablo2Path}/mods/{definedMod}/{definedMod}.mpq'):
                    external_conf = loadConfigurationFile()
                    if external_conf is not None and external_conf == f' -mod {definedMod} -txt':
                        modMenu.entryconfig(1, label=f'활성화된 모드: {definedMod}')
                    else:
                        modMenu.entryconfig(1, label=f'감지된 모드: {definedMod}')
                    modMenu.entryconfig(1, state='normal')
                    modMenu.entryconfig(1, command=SearchModInGitHub)
                else:
                    try:
                        request.urlopen('https://kr.shop.battle.net/ko-kr?from=root', timeout=1)
                        external_conf = loadConfigurationFile()
                        if external_conf is not None and external_conf == f' -mod {definedMod} -txt':
                            unloadMods = messagebox.askyesno(title='디아블로 모드 관리자', message='유효하지 않은 모드 배치가 감지되었습니다.\n게임 실행 시 모드가 적용되지 않거나 제대로 작동하지 않을 수 있습니다. 모드를 적용해제 하시겠습니까?', icon='warning')
                            if unloadMods:
                                dumpConfigurationFile('')
                                logformat(errorLevel.INFO, f'Successfully unloaded mods name: " -mod {definedMod} -txt" in {userApp}/Battle.net/Battle.net.config.')
                    except RequestError.URLError:
                        resolveTool = messagebox.askyesno(title='디아블로 모드 관리자', message='유효하지 않은 모드 배치가 감지되었습니다.\n이 문제는 주로 클라우드 스토리지에 저장된 모드에 접근할 수 없을 경우 발생할 수 있습니다. 디바이스가 인터넷에 연결되어 있는지 확인해 주세요.\n네트워크 문제해결 마법사를 실행하시겠습니까?', icon='warning')
                        if resolveTool: Popen('msdt.exe -id NetworkDiagnosticsNetworkAdapter')
                    logformat(errorLevel.WARN, f"The mod {definedMod} does not followed by path:")
                    logformat(errorLevel.WARN, f"\t- {diablo2Path}/mods/{definedMod}/{definedMod}.mpq")
                    logformat(errorLevel.WARN, f"\t- {diablo2Path}/mods/{definedMod}/{definedMod}.mpq/data")
                    modMenu.entryconfig(1, label='활성화된 모드: 검증 오류')
            else:
                logformat(errorLevel.INFO, "Diablo II Resurrected mods are not cached. Because mods was not installed yet.")
                modMenu.entryconfig(1, label='새로운 모드 탐색')
                modMenu.entryconfig(1, state='normal')
                modMenu.entryconfig(1, command=DownloadModsLink)
                definedMod = None
        else:
            logformat(errorLevel.INFO, 'Diablo II Resurrected mods directory not found.')
            modMenu.entryconfig(0, state='disabled')
            modMenu.entryconfig(1, label='새로운 모드 탐색')
            modMenu.entryconfig(1, state='normal')
            modMenu.entryconfig(1, command=DownloadModsLink)
            definedMod = None
    else:
        logformat(errorLevel.INFO, 'Diablo II Resurrected mod check disabled, because Diablo II Resurrected does not installed.')
        gameMenu.entryconfig(0, state='disabled')
        modMenu.entryconfig(0, state='disabled')
        modMenu.entryconfig(1, state='disabled')
        modMenu.entryconfig(3, state='disabled')
        modMenu.entryconfig(1, label='게임이 설치되지 않음')
        definedMod = None

    if(TestRegistryValueAsFile(r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Diablo III')):
        diablo3Path = ReturnRegistryQuery(r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Diablo III')
        gameMenu.entryconfig(1, state='normal')
    else:
        gameMenu.entryconfig(1, state='disabled')

    if(TestRegistryValueAsFile(r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Diablo IV - Server Slam')):
        diablo4Path = ReturnRegistryQuery(r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Diablo IV - Server Slam')
        gameMenu.entryconfig(2, state='normal')
    else:
        gameMenu.entryconfig(2, state='disabled')

    if(diabloExecuted): return
    if(diablo2Path is None and diablo3Path is None and diablo4Path is None):
        switchButton['state'] = "normal"
        if(TestRegistryValueAsFile(r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Battle.net')):
            switchButton['text'] = '디아블로 설치...'
            switchButton['command'] = OpenBattleNet
            fileMenu.entryconfig(0, state='normal')
        else:
            switchButton['text'] = 'Battle.net 검색'
            switchButton['command'] = ForceReload
            fileMenu.entryconfig(0, state='disabled')
    else:
        switchButton['state'] = "normal"
        switchButton['text'] = '디아블로 실행...'
        switchButton['command'] = LaunchGameAgent
        if(TestRegistryValueAsFile(r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Battle.net')):
            fileMenu.entryconfig(0, state='normal')
        else:
            fileMenu.entryconfig(0, state='disabled')

    if os.path.isdir(f'{userApp}\\Battle.net') or os.path.isdir(f'{userLocalApp}\\Battle.net') or os.path.isdir(f'{userLocalApp}\\Blizzard Entertainment'):
        fileMenu.entryconfig(1, state='normal')
    else:
        fileMenu.entryconfig(1, state='disabled')

def GetLauncherConfigurationValues():
    CheckResProgram()
    if resolutionProgram:
        global originX
        global originY
        global originFR
        global alteredX
        global alteredY
        global alteredFR

    try:
        if resolutionProgram:
            originX = loadSettings(parentLocation.UserLocalAppData, ["ScreenResolution", "OriginResolutionVector", "OriginX"])
            originY = loadSettings(parentLocation.UserLocalAppData, ["ScreenResolution", "OriginResolutionVector", "OriginY"])
            originFR = loadSettings(parentLocation.UserLocalAppData, ["ScreenResolution", "OriginResolutionVector", "OriginFR"])

            alteredX = loadSettings(parentLocation.UserLocalAppData, ["ScreenResolution", "AlteredResolutionVector", "AlteredX"])
            alteredY = loadSettings(parentLocation.UserLocalAppData, ["ScreenResolution", "AlteredResolutionVector", "AlteredY"])
            alteredFR = loadSettings(parentLocation.UserLocalAppData, ["ScreenResolution", "AlteredResolutionVector", "AlteredFR"])

            if originX is None or originY is None or originFR is None or alteredX is None or alteredY is None or alteredFR is None:
                originX = loadSettings(parentLocation.ProgramData, ["ScreenResolution", "OriginResolutionVector", "OriginX"])
                originY = loadSettings(parentLocation.ProgramData, ["ScreenResolution", "OriginResolutionVector", "OriginY"])
                originFR = loadSettings(parentLocation.ProgramData, ["ScreenResolution", "OriginResolutionVector", "OriginFR"])

                alteredX = loadSettings(parentLocation.ProgramData, ["ScreenResolution", "AlteredResolutionVector", "AlteredX"])
                alteredY = loadSettings(parentLocation.ProgramData, ["ScreenResolution", "AlteredResolutionVector", "AlteredY"])
                alteredFR = loadSettings(parentLocation.ProgramData, ["ScreenResolution", "AlteredResolutionVector", "AlteredFR"])

            logformat(errorLevel.INFO, 'parameter conversion succeed')
        else:
            logformat(errorLevel.INFO, 'QRes not detected. Skipping parameter conversion.')

        if resolutionProgram:
            logformat(errorLevel.INFO, f'Default resolution: {int(originX)} X {int(originY)} {float(originFR)}Hz')
            logformat(errorLevel.INFO, f'Convert resolution: {int(alteredX)} X {int(alteredY)} {float(alteredFR)}Hz')
            if (call(f'QRes /L | findstr /r "{originX}x" |findstr /r "{originY}," | findstr /r "\\<{originFR}\\>" > NUL 2>&1', shell=True) != 0) or (call(f'QRes /L | findstr /r "{alteredX}x" |findstr /r "{alteredY}," | findstr /r "\\<{alteredFR}\\>" > NUL 2>&1', shell=True) != 0):
                messagebox.showwarning('디아블로 런처', '일부 해상도가 이 디스플레이와 호환되지 않습니다. 시스템 환경 설정에서 지원하는 해상도를 확인하시기 바랍니다.')
                logformat(errorLevel.WARN, 'Some resolution scale does not compatibility this display. Please enter another resolution scale.')

    except (ValueError, TypeError, AttributeError) as error:
        messagebox.showerror('디아블로 런처', f'해상도 벡터 파싱중 예외가 발생하였습니다. 해상도 벡터가 올바르게 설정 되어있는지 다시 한번 확인해 주세요. Exception code: {error}')
        switchButton['state'] = "disabled"
        originX = None
        originY = None
        originFR = None
        alteredX = None
        alteredY = None
        alteredFR = None
    finally:
        if resolutionProgram:
            logformat(errorLevel.INFO, f'Default resolution: {originX} X {originY} {originFR}Hz')
            logformat(errorLevel.INFO, f'Convert resolution: {alteredX} X {alteredY} {alteredFR}Hz')

def SetLauncherConfigurationValues(*args):
    global modsPreferPreviousSetting
    global modsInstalledList
    global modsPreferOptionMenu

    global testResOriginX
    global testResOriginY
    global testResOriginFR
    global testResAlteredX
    global testResAlteredY
    global testResAlteredFR
    global modsMuteSettings
    global verboseSettings
    global resIgnoreAlert

    envWindow = Toplevel()
    envWindow.title('디아블로 런처 설정')
    envWindow.geometry(f"380x230+{int(root.winfo_x() + root.winfo_reqwidth() / 2 - 380 / 2)}+{int(root.winfo_y() + root.winfo_reqheight() / 2 - 230 / 2)}")
    envWindow.resizable(False, False)
    envWindow.attributes('-toolwindow', True)
    envWindow.attributes('-topmost', 'true')

    currentTarget = parentLocation.UserLocalAppData

    resolutionText = Label(envWindow, text='')

    modsCurrentSelectMenu = StringVar()
    originXtext = Label(envWindow, text='기본 X')
    originYtext = Label(envWindow, text=' Y')
    originFRtext = Label(envWindow, text=' FR')
    envOriginX = Entry(envWindow, width=5)
    envOriginY = Entry(envWindow, width=5)
    envOriginFR = Entry(envWindow, width=4)

    alteredXtext = Label(envWindow, text='변경 X')
    alteredYtext = Label(envWindow, text=' Y')
    alteredFRtext = Label(envWindow, text=' FR')
    envAlteredX = Entry(envWindow, width=5)
    envAlteredY = Entry(envWindow, width=5)
    envAlteredFR = Entry(envWindow, width=4)

    modsMuteSettings = IntVar()
    verboseSettings = IntVar()
    resIgnoreAlert = IntVar()

    resolutionText.grid(row=0, column=0, columnspan=5)
    originXtext.grid(row=1, column=0)
    envOriginX.grid(row=1, column=1)
    originYtext.grid(row=1, column=2)
    envOriginY.grid(row=1, column=3)
    originFRtext.grid(row=1, column=4)
    envOriginFR.grid(row=1, column=5)

    alteredXtext.grid(row=2, column=0)
    envAlteredX.grid(row=2, column=1)
    alteredYtext.grid(row=2, column=2)
    envAlteredY.grid(row=2, column=3)
    alteredFRtext.grid(row=2, column=4)
    envAlteredFR.grid(row=2, column=5)

    def updateResSettings():
        global testResOriginX
        global testResOriginY
        global testResOriginFR
        global testResAlteredX
        global testResAlteredY
        global testResAlteredFR

        testResOriginX = loadSettings(currentTarget, ["ScreenResolution", "OriginResolutionVector", "OriginX"])
        testResOriginY = loadSettings(currentTarget, ["ScreenResolution", "OriginResolutionVector", "OriginY"])
        testResOriginFR = loadSettings(currentTarget, ["ScreenResolution", "OriginResolutionVector", "OriginFR"])
        testResAlteredX = loadSettings(currentTarget, ["ScreenResolution", "AlteredResolutionVector", "AlteredX"])
        testResAlteredY = loadSettings(currentTarget, ["ScreenResolution", "AlteredResolutionVector", "AlteredY"])
        testResAlteredFR = loadSettings(currentTarget, ["ScreenResolution", "AlteredResolutionVector", "AlteredFR"])

    if resolutionProgram:
        resolutionText['text'] = '해상도 벡터'
        updateResSettings()
        if(testResOriginX is None or testResOriginY is None or testResOriginFR is None or testResAlteredX is None or testResAlteredY is None or testResAlteredFR is None):
            currentTarget = parentLocation.ProgramData
            updateResSettings()
            if(testResOriginX is None or testResOriginY is None or testResOriginFR is None or testResAlteredX is None or testResAlteredY is None or testResAlteredFR is None):
                messagebox.showwarning('해상도 벡터 편집기', '현재 해상도 벡터가 설정되어 있지 않습니다. 해상도 벡터를 설정해 주세요.')
                currentTarget = parentLocation.UserLocalAppData
            else:
                envOriginX.insert(0, testResOriginX)
                envOriginY.insert(0, testResOriginY)
                envOriginFR.insert(0, testResOriginFR)
                envAlteredX.insert(0, testResAlteredX)
                envAlteredY.insert(0, testResAlteredY)
                envAlteredFR.insert(0, testResAlteredFR)
        else:
            envOriginX.insert(0, testResOriginX)
            envOriginY.insert(0, testResOriginY)
            envOriginFR.insert(0, testResOriginFR)
            envAlteredX.insert(0, testResAlteredX)
            envAlteredY.insert(0, testResAlteredY)
            envAlteredFR.insert(0, testResAlteredFR)

        envOriginX['state'] = 'normal'
        envOriginY['state'] = 'normal'
        envOriginFR['state'] = 'normal'
        envAlteredX['state'] = 'normal'
        envAlteredY['state'] = 'normal'
        envAlteredFR['state'] = 'normal'
    else:
        resolutionText['text'] = '해상도 변경 프로그램 미설치'
        envOriginX['state'] = 'disabled'
        envOriginY['state'] = 'disabled'
        envOriginFR['state'] = 'disabled'
        envAlteredX['state'] = 'disabled'
        envAlteredY['state'] = 'disabled'
        envAlteredFR['state'] = 'disabled'

    def commitResolutionValue():
        if not testResolutionValue(): return
        try:
            dumpSettings(currentTarget, ["ScreenResolution", "OriginResolutionVector", "OriginX"], envOriginX.get())
            dumpSettings(currentTarget, ["ScreenResolution", "OriginResolutionVector", "OriginY"], envOriginY.get())
            dumpSettings(currentTarget, ["ScreenResolution", "OriginResolutionVector", "OriginFR"], envOriginFR.get())

            dumpSettings(currentTarget, ["ScreenResolution", "AlteredResolutionVector", "AlteredX"], envAlteredX.get())
            dumpSettings(currentTarget, ["ScreenResolution", "AlteredResolutionVector", "AlteredY"], envAlteredY.get())
            dumpSettings(currentTarget, ["ScreenResolution", "AlteredResolutionVector", "AlteredFR"], envAlteredFR.get())
            UpdateStatusValue()
            ReloadStatusBar()
            envWindow.destroy()
        except AttributeError as error:
            logformat(errorLevel.ERR, f"could not save screen resolution value: {error}")
            UpdateStatusValue()

    def screenResolutionSwitcher():
        if not testResolutionValue(): return
        envOriginX['state'] = 'disabled'
        envOriginY['state'] = 'disabled'
        envOriginFR['state'] = 'disabled'
        envAlteredX['state'] = 'disabled'
        envAlteredY['state'] = 'disabled'
        envAlteredFR['state'] = 'disabled'
        Popen(f'QRes -X {envAlteredX.get()} -Y {envAlteredY.get()} -R {envAlteredFR.get()} > NUL 2>&1', shell=True)
        time.sleep(5)
        Popen(f'QRes -X {envOriginX.get()} -Y {envOriginY.get()} -R {envOriginFR.get()} > NUL 2>&1', shell=True)
        envOriginX['state'] = 'normal'
        envOriginY['state'] = 'normal'
        envOriginFR['state'] = 'normal'
        envAlteredX['state'] = 'normal'
        envAlteredY['state'] = 'normal'
        envAlteredFR['state'] = 'normal'

    def testResolutionValue():
        if envOriginX.get() == '' or envOriginY.get() == '' or envOriginFR.get() == '' or envAlteredX.get() == '' or envAlteredY.get() == '' or envAlteredFR.get() == '':
            messagebox.showwarning('디아블로 설정', '일부 해상도 값이 누락되었습니다.')
            logformat(errorLevel.WARN, 'some screen resolution value can not be None.')
            envWindow.after(1, envWindow.focus_force())
            return False

        if (call(f'QRes /L | findstr /r "{envOriginX.get()}x" |findstr /r "{envOriginY.get()}," | findstr /r "\\<{envOriginFR.get()}\\>" > NUL 2>&1', shell=True) != 0) or (call(f'QRes /L | findstr /r "{envAlteredX.get()}x" |findstr /r "{envAlteredY.get()}," | findstr /r "\\<{envAlteredFR.get()}\\>" > NUL 2>&1', shell=True) != 0):
            messagebox.showwarning('해상도 벡터 편집기', '일부 해상도가 이 디스플레이와 호환되지 않습니다. 현재 디스플레이와 호환되는 다른 해상도를 입력해 주세요.')
            logformat(errorLevel.WARN, 'Some resolution scale does not compatibility this display. Please enter another resolution scale.')
            envWindow.after(1, envWindow.focus_force())
            return False

        return True

    def changeIgnoreResAlert():
        dumpSettings(parentLocation.UserLocalAppData, ["ScreenResolution", "IgnoreResProgramInstallDialog"], resIgnoreAlert.get() == 1)
        resIgnoreAlert.set(1 if loadSettings(parentLocation.ProgramData, ["ScreenResolution", "IgnoreResProgramInstallDialog"]) or loadSettings(parentLocation.UserLocalAppData, ["ScreenResolution", "IgnoreResProgramInstallDialog"]) else 0)
        if loadSettings(parentLocation.ProgramData, ["ScreenResolution", "IgnoreResProgramInstallDialog"]):
            resDialogIgnoreCheckbox['state'] = 'disabled'
        else:
            resDialogIgnoreCheckbox['state'] = 'normal'

    if resolutionProgram:
        resTestBtn = Button(envWindow, text='해상도 테스트', command=screenResolutionSwitcher, state='normal')
        resCommitBtn = Button(envWindow, text='적용', command=commitResolutionValue, state='normal')

    else:
        resTestBtn = Button(envWindow, text='해상도 테스트', command=screenResolutionSwitcher, state='disabled')
        resCommitBtn = Button(envWindow, text='적용', command=commitResolutionValue, state='disabled')

    resIgnoreAlert.set(1 if loadSettings(parentLocation.ProgramData, ["ScreenResolution", "IgnoreResProgramInstallDialog"]) or loadSettings(parentLocation.UserLocalAppData, ["ScreenResolution", "IgnoreResProgramInstallDialog"]) else 0)
    if loadSettings(parentLocation.ProgramData, ["ScreenResolution", "IgnoreResProgramInstallDialog"]):
        resDialogIgnoreCheckbox = Checkbutton(envWindow, text='설치 알림 뮤트', variable=resIgnoreAlert, onvalue=True, offvalue=False, command=changeIgnoreResAlert, state='disabled')
    else:
        resDialogIgnoreCheckbox = Checkbutton(envWindow, text='설치 알림 뮤트', variable=resIgnoreAlert, onvalue=True, offvalue=False, command=changeIgnoreResAlert, state='normal')

    resTestBtn.grid(row=3, column=0, pady=10)
    resCommitBtn.grid(row=3, column=1, pady=10)
    resDialogIgnoreCheckbox.grid(row=3, column=3, columnspan=2, pady=10)

    def applyPreferMods():
        dumpSettings(parentLocation.UserLocalAppData, ["ModsManager", "PreferMods"], modsCurrentSelectMenu.get())
        FindGameInstalled()
        GetModDetails()
        if isinstance(definedMod, list) and modsCurrentSelectMenu.get() != "-- 선택 --":
            messagebox.showwarning('모드 관리자', f'현재 입력한 {modsCurrentSelectMenu.get()} 모드에 접근 권한이 없거나 정상적으로 설치되지 않은 것 같습니다.')
        updateModsData()
        testModsApply()

    def testModsApply(*args):
        modsMuteConfig = loadSettings(parentLocation.UserLocalAppData, ["ModsManager", "IgnoreModsMergeDialog"])
        if modsMuteConfig and modsPreferPreviousSetting is None or modsCurrentSelectMenu.get() == modsPreferPreviousSetting or modsCurrentSelectMenu.get() == "-- 선택 --":
            modsPreferApply['state'] = 'disabled'
        else:
            modsPreferApply['state'] = 'normal'

        if modsMuteConfig and modsPreferPreviousSetting is None:
            modsPreferOptionMenu['state'] = 'disabled'
        else:
            modsPreferOptionMenu['state'] = 'normal'

    def updateModsData():
        global modsPreferPreviousSetting
        global modsInstalledList

        modsPreferPreviousSetting = loadSettings(parentLocation.UserLocalAppData, ["ModsManager", "PreferMods"])
        if os.path.isdir(f'{diablo2Path}/mods'):
            listDir = os.listdir(f'{diablo2Path}/mods')
            modsInstalledList = []

            for modsName in listDir:
                if os.path.isdir(f'{diablo2Path}/mods/{modsName}/{modsName}.mpq/data') or os.path.isfile(f'{diablo2Path}/mods/{modsName}/{modsName}.mpq'):
                    modsInstalledList.append(modsName)
                else:
                    logformat(errorLevel.WARN, f"The mod {modsName} does not followed by path:")
                    logformat(errorLevel.WARN, f"\t- {modsName}/mods/{modsName}/{modsName}.mpq")
                    logformat(errorLevel.WARN, f"\t- {modsName}/mods/{modsName}/{modsName}.mpq/data")

            if len(modsInstalledList) == 0:
                return False

            if modsPreferPreviousSetting is not None:
                for value in modsInstalledList:
                    if modsPreferPreviousSetting == value:
                        modsCurrentSelectMenu.set(value)
                        break

                currentModsConfiguration = loadConfigurationFile()
                if currentModsConfiguration is not None and definedMod is not None and currentModsConfiguration == f' -mod {definedMod} -txt':
                    logformat(errorLevel.WARN, f'Prefer mods OptionMenu was disabled. reason: {definedMod} mod was already defined Battle.net external command parameter.')
                    return False
            else:
                modsCurrentSelectMenu.set('-- 선택 --')

            return True
        else:
            return False

    modsPreferText = Label(envWindow, text='선호하는 모드명')
    modsPreferApply = Button(envWindow, text='적용', command=applyPreferMods)

    if updateModsData():
        modsPreferOptionMenu = OptionMenu(envWindow, modsCurrentSelectMenu, *modsInstalledList, command=testModsApply)
        modsPreferOptionMenu.configure(state='normal')
        testModsApply()
    else:
        modsPreferOptionMenu = OptionMenu(envWindow, modsCurrentSelectMenu, [], command=testModsApply)
        modsPreferOptionMenu.configure(state='disabled')
        modsPreferApply['state'] = 'disabled'

    modsPreferOptionMenu.config(width=20)

    modsPreferText.grid(row=4, column=0, pady=10)
    modsPreferOptionMenu.grid(row=4, column=1, columnspan=4, pady=10)
    modsPreferApply.grid(row=4, column=5, pady=10)

    def modsMuteSettingsApply():
        dumpSettings(parentLocation.UserLocalAppData, ["ModsManager", "IgnoreModsMergeDialog"], modsMuteSettings.get() == 1)
        modsMuteSettings.set(1 if loadSettings(parentLocation.UserLocalAppData, ["ModsManager", "IgnoreModsMergeDialog"]) else 0)

    modsMuteSettings.set(1 if loadSettings(parentLocation.UserLocalAppData, ["ModsManager", "IgnoreModsMergeDialog"]) else 0)
    modsMuteCheckBox = Checkbutton(envWindow, text="모드 병합 알림 뮤트", variable=modsMuteSettings, onvalue=True, offvalue=False, command=modsMuteSettingsApply)
    modsMuteCheckBox.grid(row=5, column=0, columnspan=2, padx=5)

    def changeVerboseLogSettingsApply():
        dumpSettings(parentLocation.UserLocalAppData, ["General", "LoggingInfoLevel"], verboseSettings.get() == 1)
        verboseSettings.set(1 if loadSettings(parentLocation.UserLocalAppData, ["General", "LoggingInfoLevel"]) else 0)
        if verboseSettings.get() == 1:
            os.environ['LOG_VERBOSE_LEVEL'] = 'verbose'
        else:
            os.environ.pop('LOG_VERBOSE_LEVEL')

    verboseSettings.set(1 if loadSettings(parentLocation.UserLocalAppData, ["General", "LoggingInfoLevel"]) else 0)
    verboseCheckbox = Checkbutton(envWindow, text="디버그 메시지", variable=verboseSettings, onvalue=True, offvalue=False, command=changeVerboseLogSettingsApply)
    verboseCheckbox.grid(row=7, column=0, columnspan=1, padx=5, pady=10)

    systemConfigFileEdit = Button(envWindow, text='전역 설정 편집', command=lambda: os.startfile(f'{os.environ.get("ProgramData")}/DiabloLauncher/DiabloLauncher.config'))
    systemConfigFileEdit.grid(row=7, column=1, columnspan=2, pady=10)

    localConfigFileEdit = Button(envWindow, text='지역 설정 편집', command=lambda: os.startfile(f'{os.environ.get("LocalAppData")}/DiabloLauncher/DiabloLauncher.config'))
    localConfigFileEdit.grid(row=7, column=3, columnspan=2, pady=10)


    if(CheckDarkMode()):
        envWindow['background'] = '#272727'
        originXtext['background'] = '#272727'
        originXtext['foreground'] = '#FFFFFF'
        resolutionText['background'] = '#272727'
        resolutionText['foreground'] = '#FFFFFF'
        envOriginX['disabledbackground'] = '#272727'
        envOriginX['background'] = '#272727'
        envOriginX['foreground'] = '#FFFFFF'
        originYtext['background'] = '#272727'
        originYtext['foreground'] = '#FFFFFF'
        envOriginY['disabledbackground'] = '#272727'
        envOriginY['background'] = '#272727'
        envOriginY['foreground'] = '#FFFFFF'
        originFRtext['background'] = '#272727'
        originFRtext['foreground'] = '#FFFFFF'
        envOriginFR['disabledbackground'] = '#272727'
        envOriginFR['background'] = '#272727'
        envOriginFR['foreground'] = '#FFFFFF'
        alteredXtext['background'] = '#272727'
        alteredXtext['foreground'] = '#FFFFFF'
        envAlteredX['disabledbackground'] = '#272727'
        envAlteredX['background'] = '#272727'
        envAlteredX['foreground'] = '#FFFFFF'
        alteredYtext['background'] = '#272727'
        alteredYtext['foreground'] = '#FFFFFF'
        envAlteredY['disabledbackground'] = '#272727'
        envAlteredY['background'] = '#272727'
        envAlteredY['foreground'] = '#FFFFFF'
        alteredFRtext['background'] = '#272727'
        alteredFRtext['foreground'] = '#FFFFFF'
        envAlteredFR['disabledbackground'] = '#272727'
        envAlteredFR['background'] = '#272727'
        envAlteredFR['foreground'] = '#FFFFFF'
        modsPreferText['background'] = '#272727'
        modsPreferText['foreground'] = '#FFFFFF'
        resCommitBtn['background'] = '#272727'
        resCommitBtn['activebackground'] = '#272727'
        resCommitBtn['foreground'] = '#FFFFFF'
        resCommitBtn['activeforeground'] = '#FFFFFF'
        resTestBtn['background'] = '#272727'
        resTestBtn['activebackground'] = '#272727'
        resTestBtn['foreground'] = '#FFFFFF'
        resTestBtn['activeforeground'] = '#FFFFFF'
        modsPreferApply['background'] = '#272727'
        modsPreferApply['activebackground'] = '#272727'
        modsPreferApply['foreground'] = '#FFFFFF'
        modsPreferApply['activeforeground'] = '#FFFFFF'
        modsPreferOptionMenu['background'] = '#272727'
        modsPreferOptionMenu['activebackground'] = '#272727'
        modsPreferOptionMenu['foreground'] = '#FFFFFF'
        modsPreferOptionMenu['activeforeground'] = '#FFFFFF'
        systemConfigFileEdit['background'] = '#272727'
        systemConfigFileEdit['activebackground'] = '#272727'
        systemConfigFileEdit['foreground'] = '#FFFFFF'
        systemConfigFileEdit['activeforeground'] = '#FFFFFF'
        localConfigFileEdit['background'] = '#272727'
        localConfigFileEdit['activebackground'] = '#272727'
        localConfigFileEdit['foreground'] = '#FFFFFF'
        localConfigFileEdit['activeforeground'] = '#FFFFFF'
        modsMuteCheckBox['background'] = '#272727'
        modsMuteCheckBox['activebackground'] = '#272727'
        modsMuteCheckBox['selectcolor'] = '#272727'
        modsMuteCheckBox['foreground'] = '#FFFFFF'
        modsMuteCheckBox['activeforeground'] = '#FFFFFF'
        verboseCheckbox['background'] = '#272727'
        verboseCheckbox['activebackground'] = '#272727'
        verboseCheckbox['selectcolor'] = '#272727'
        verboseCheckbox['foreground'] = '#FFFFFF'
        verboseCheckbox['activeforeground'] = '#FFFFFF'
        resDialogIgnoreCheckbox['background'] = '#272727'
        resDialogIgnoreCheckbox['activebackground'] = '#272727'
        resDialogIgnoreCheckbox['selectcolor'] = '#272727'
        resDialogIgnoreCheckbox['foreground'] = '#FFFFFF'
        resDialogIgnoreCheckbox['activeforeground'] = '#FFFFFF'
    else:
        envWindow['background'] = '#F0F0F0'
        originXtext['background'] = '#F0F0F0'
        originXtext['foreground'] = '#000000'
        resolutionText['background'] = '#F0F0F0'
        resolutionText['foreground'] = '#000000'
        envOriginX['disabledbackground'] = '#F0F0F0'
        envOriginX['background'] = '#F0F0F0'
        envOriginX['foreground'] = '#000000'
        originYtext['background'] = '#F0F0F0'
        originYtext['foreground'] = '#000000'
        envOriginY['disabledbackground'] = '#F0F0F0'
        envOriginY['background'] = '#F0F0F0'
        envOriginY['foreground'] = '#000000'
        originFRtext['background'] = '#F0F0F0'
        originFRtext['foreground'] = '#000000'
        envOriginFR['disabledbackground'] = '#F0F0F0'
        envOriginFR['background'] = '#F0F0F0'
        envOriginFR['foreground'] = '#000000'
        alteredXtext['background'] = '#F0F0F0'
        alteredXtext['foreground'] = '#000000'
        envAlteredX['disabledbackground'] = '#F0F0F0'
        envAlteredX['background'] = '#F0F0F0'
        envAlteredX['foreground'] = '#000000'
        alteredYtext['background'] = '#F0F0F0'
        alteredYtext['foreground'] = '#000000'
        envAlteredY['disabledbackground'] = '#F0F0F0'
        envAlteredY['background'] = '#F0F0F0'
        envAlteredY['foreground'] = '#000000'
        alteredFRtext['background'] = '#F0F0F0'
        alteredFRtext['foreground'] = '#000000'
        envAlteredFR['disabledbackground'] = '#F0F0F0'
        envAlteredFR['background'] = '#F0F0F0'
        envAlteredFR['foreground'] = '#000000'
        modsPreferText['background'] = '#F0F0F0'
        modsPreferText['foreground'] = '#000000'
        resCommitBtn['background'] = '#F0F0F0'
        resCommitBtn['activebackground'] = '#F0F0F0'
        resCommitBtn['foreground'] = '#000000'
        resCommitBtn['activeforeground'] = '#000000'
        resTestBtn['background'] = '#F0F0F0'
        resTestBtn['activebackground'] = '#F0F0F0'
        resTestBtn['foreground'] = '#000000'
        resTestBtn['activeforeground'] = '#000000'
        modsPreferApply['background'] = '#F0F0F0'
        modsPreferApply['activebackground'] = '#F0F0F0'
        modsPreferApply['foreground'] = '#000000'
        modsPreferApply['activeforeground'] = '#000000'
        systemConfigFileEdit['background'] = '#F0F0F0'
        systemConfigFileEdit['activebackground'] = '#F0F0F0'
        systemConfigFileEdit['foreground'] = '#000000'
        systemConfigFileEdit['activeforeground'] = '#000000'
        localConfigFileEdit['background'] = '#F0F0F0'
        localConfigFileEdit['activebackground'] = '#F0F0F0'
        localConfigFileEdit['foreground'] = '#000000'
        localConfigFileEdit['activeforeground'] = '#000000'
        modsPreferOptionMenu['background'] = '#F0F0F0'
        modsPreferOptionMenu['activebackground'] = '#F0F0F0'
        modsPreferOptionMenu['foreground'] = '#000000'
        modsPreferOptionMenu['activeforeground'] = '#000000'
        modsMuteCheckBox['background'] = '#F0F0F0'
        modsMuteCheckBox['activebackground'] = '#F0F0F0'
        modsMuteCheckBox['selectcolor'] = '#F0F0F0'
        modsMuteCheckBox['foreground'] = '#000000'
        modsMuteCheckBox['activeforeground'] = '#000000'
        verboseCheckbox['background'] = '#F0F0F0'
        verboseCheckbox['activebackground'] = '#F0F0F0'
        verboseCheckbox['selectcolor'] = '#F0F0F0'
        verboseCheckbox['foreground'] = '#000000'
        verboseCheckbox['activeforeground'] = '#000000'
        resDialogIgnoreCheckbox['background'] = '#F0F0F0'
        resDialogIgnoreCheckbox['activebackground'] = '#F0F0F0'
        resDialogIgnoreCheckbox['selectcolor'] = '#F0F0F0'
        resDialogIgnoreCheckbox['foreground'] = '#000000'
        resDialogIgnoreCheckbox['activeforeground'] = '#000000'

    envWindow.mainloop()

def RequirementCheck():
    if not resolutionProgram:
        logformat(errorLevel.WARN, f'QRes not installed or not in...\n\t- C:\\Windows\\System32\n\t- {userLocalApp}/Program/Common/QRes.exe')
        res_alert = loadSettings(parentLocation.UserLocalAppData, ["ScreenResolution", "IgnoreResProgramInstallDialog"]) or loadSettings(parentLocation.ProgramData, ["ScreenResolution", "IgnoreResProgramInstallDialog"])
        if res_alert is None or res_alert is False:
            msg_box = messagebox.askquestion('디아블로 런처', '해상도를 변경하려면 QRes를 먼저 설치하여야 합니다. 지금 QRes를 다운로드 하시겠습니까?', icon='question')
            if msg_box == 'yes':
                webbrowser.open('https://www.softpedia.com/get/Multimedia/Video/Other-VIDEO-Tools/QRes.shtml')
        else:
            logformat(errorLevel.WARN, 'QRes install check dialog rejected due to IgnoreResProgramInstallDialog setting is true.\n\tPlease install QRes if would you like change display resolution.')
            print(f"\t{color.YELLOW.value}URL:{color.BLUE.value} https://www.softpedia.com/get/Multimedia/Video/Other-VIDEO-Tools/QRes.shtml{color.RESET.value}")
    if diablo2Path is None and diablo3Path is None and diablo4Path is None:
        logformat(errorLevel.WARN, 'The game does not exist in registry.')
        messagebox.showwarning('디아블로 런처', '이 컴퓨터에 디아블로 게임을 찾을 수 없습니다. 자세한 사항은 GitHub에 방문해 주세요.')

def UpdateStatusValue():
    FindGameInstalled()
    GetLauncherConfigurationValues()
    now = datetime.now()
    cnt_time = now.strftime("%H:%M:%S")

    if resolutionProgram:
        status['text'] = f"\n정보 - {cnt_time}에 업데이트\n해상도 변경 지원됨: 예\n해상도 벡터: {f'{originX}x{originY} - {alteredX}x{alteredY}'}\n현재 해상도: {f'{alteredX}x{alteredY} {alteredFR}Hz' if diabloExecuted else f'{originX}x{originY} {originFR}Hz'}\n디아블로 실행: {'예' if diabloExecuted else '아니요'}\n"
    else:
        status['text'] = f"\n정보 - {cnt_time}에 업데이트\n해상도 변경 지원됨: 아니요\n\n\n디아블로 실행: {'예' if diabloExecuted else '아니요'}\n"

def ReloadStatusBar():
    loadStart = time.time()

    if os.path.isdir(f'{userApp}/DiabloLauncher'):
        aboutMenu.entryconfig(3, state='normal')
    else:
        aboutMenu.entryconfig(3, state='disabled')

    count, stat_max, stat_sum, stat_avg = LoadGameRunningTime()
    maxTime = FormatTime(stat_max, False)
    avgTime = FormatTime(stat_avg, False)
    sumTime = FormatTime(stat_sum, False)
    loadEnd = time.time()

    elapsedTime = loadEnd - loadStart
    if elapsedTime > loadWaitTime:
        logformat(errorLevel.WARN, f'The request timeout when loading game data {userApp}/DiabloLauncher/runtime.log file.')
        logformat(errorLevel.INFO, f"Loading game data elapsed time was{'{:5.2f}'.format(elapsedTime)} seconds. But, current timeout setting is {loadWaitTime} seconds.")
        logformat(errorLevel.INFO, f'NOTE: The {userApp}/DiabloLauncher/runtime.log contents cleared.')
        ClearGameRunningTime()
    elif elapsedTime > (loadWaitTime / 2):
        logformat(errorLevel.WARN, f'The request job too slow when loading game data {userApp}/DiabloLauncher/runtime.log file.')
        logformat(errorLevel.INFO, f"Loading game data elapsed time was{'{:5.2f}'.format(elapsedTime)} seconds, and current timeout setting is {loadWaitTime} seconds.")
        logformat(errorLevel.INFO, f'NOTE: {userApp}/DiabloLauncher/runtime.log contents will clear when this issues raised again.')
    else:
        logformat(errorLevel.INFO, f"Loading game data elapsed time was{'{:5.2f}'.format(elapsedTime)} seconds.")

    logformat(errorLevel.INFO, f'Previous game time for max session: {maxTime}')
    logformat(errorLevel.INFO, f'Previous game time for avg session: {avgTime}')
    logformat(errorLevel.INFO, f'Previous game time for sum session: {sumTime}')

    if count >= 10 or len(f"세션: {count}개 | 최고: {maxTime} | 평균: {avgTime} | 합계: {sumTime}") > 57:
        statusbar['text'] = f"세션: {count}개 | 최고: {maxTime} | 평균: {avgTime} | 합계: {sumTime}"
        statusbar['anchor'] = CENTER
        toolsMenu.entryconfig(7, state='normal')
    elif count >= 3:
        statusbar['text'] = f"{check_terminal_output('git rev-parse --short HEAD')} | 세션: {count}개 | 최고: {maxTime} | 평균: {avgTime} | 합계: {sumTime}"
        statusbar['anchor'] = CENTER
        toolsMenu.entryconfig(7, state='normal')
    elif count >= 2:
        statusbar['text'] = f"{check_terminal_output('git rev-parse --short HEAD')} | 세션: {count}개 | 최고: {maxTime} | 평균 표시까지 {3 - count}개 남음 | 합계: {sumTime}"
        statusbar['anchor'] = CENTER
        toolsMenu.entryconfig(7, state='normal')
    elif count >= 0:
        statusbar['text'] = f"{check_terminal_output('git rev-parse --short HEAD')} | 세션: {count}개 | 통계를 표시하려면 {2 - count}개의 세션이 더 필요합니다"
        statusbar['anchor'] = W
        if count > 0:
            toolsMenu.entryconfig(7, state='normal')
        else:
            toolsMenu.entryconfig(7, state='disabled')

def OpenBattleNet(*args):
    result = check_terminal_output('tasklist | findstr "Battle.net.exe > NUL 2>&1', True)
    if result is None:
        OpenProgramUsingRegistry(r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Battle.net')
        time.sleep(5)
    else:
        logformat(errorLevel.ERR, "Unable to open Battle.net. reason: another Battle.net agent detected.")
        messagebox.showerror(title='디아블로 런처', message='Battle.net이 이미 실행 중 입니다. 예기치 않은 오류를 최소화 하기위해 먼저 Battle.net을 종료한 후 다시 시도해 주세요.')
    FindGameInstalled()

def ForceReload(*args):
    UpdateStatusValue()
    ReloadStatusBar()
    FindGameInstalled()
    CheckDarkMode()

def init():
    global welcome
    global info
    global notice
    global switchButton
    global emergencyButton
    global status
    global statusbar
    global fileMenu
    global toolsMenu
    global aboutMenu
    global gameMenu
    global modMenu
    global root
    global launch

    root = Tk()
    root.withdraw()
    launch = Tk()
    launch.withdraw()

    root.title("디아블로 런처")
    previousWindowPosition = loadSettings(parentLocation.UserAppData, ["General", "LastWindowPosition"])
    if previousWindowPosition is not None:
        root.geometry(f"520x360+{previousWindowPosition[0]}+{previousWindowPosition[1]}")
    else:
        root.geometry("520x360+100+100")
    root.deiconify()
    root.resizable(False, False)
    root.attributes('-toolwindow', True)
    launch.title('무제')
    launch.geometry("300x125+200+200")
    launch.resizable(False, False)
    launch.attributes('-toolwindow', True)
    root.after(1, root.focus_force())

    rootFrame = Frame(root)

    launch.protocol("WM_DELETE_WINDOW", HideWindow)
    root.protocol("WM_DELETE_WINDOW", ExitProgram)
    signal.signal(signal.SIGINT, InterruptProgram)

    agentLaunched = loadSettings(parentLocation.UserAppData, ["General", "AgentLaunched"])
    if agentLaunched is not None and agentLaunched is False:
        dumpSettings(parentLocation.UserAppData, ["General", "AgentLaunched"], True)
    elif agentLaunched is not None and agentLaunched is True:
        msg_box = messagebox.askyesno(title='디아블로 런처', message='여러개의 디아블로 런처를 실행시 불안정해질 수 있습니다. 그래도 디아블로 런처를 실행 하시겠습니까?')
        if not msg_box:
            logformat(errorLevel.FATL, 'Unable to launch DiabloLauncher. reason: User abort DiabloLauncher process.')
            exit(1)

    def ResetGameStatus():
        count, stat_max, stat_sum, stat_avg = LoadGameRunningTime()
        if count > 0:
            msg_box = messagebox.askyesno(title='디아블로 런처', message=f'통계 재설정을 수행할 경우 {count}개의 세션이 영원히 유실되며 되돌릴 수 없습니다. 만약의 경우를 대비하여 {userApp}/DiabloLauncher/runtime.log 파일을 백업하시기 바랍니다. 통계 재설정을 계속 하시겠습니까? ')
            if msg_box:
                ClearGameRunningTime()
                ForceReload()

    def OpenGameStatusDir():
        if os.path.isdir(f'{userApp}/DiabloLauncher'):
            logformat(errorLevel.INFO, f'The {userApp}/DiabloLauncher directory exist. The target directory will now open.')
            os.startfile(f'"{userApp}/DiabloLauncher"')

    def OpenD2RDir():
        if diablo2Path is not None and os.path.isdir(diablo2Path):
            logformat(errorLevel.INFO, f'The {diablo2Path} directory exist. The target directory will now open.')
            os.startfile(f'"{diablo2Path}"')

    def OpenD3Dir():
        if diablo3Path is not None and os.path.isdir(diablo3Path):
            logformat(errorLevel.INFO, f'The {diablo3Path} directory exist. The target directory will now open.')
            os.startfile(f'"{diablo3Path}"')

    def OpenD4Dir():
        if diablo4Path is not None and os.path.isdir(diablo4Path):
            logformat(errorLevel.INFO, f'The {diablo4Path} directory exist. The target directory will now open.')
            os.startfile(f'"{diablo4Path}"')

    def openControlPanel():
        Popen('control.exe appwiz.cpl', shell=True)

    def OpenDevIssues(*args):
        logLevel = loadSettings(parentLocation.UserLocalAppData, ["General", "LoggingInfoLevel"])
        if logLevel is None or logLevel is False or releaseMode: return

        now = datetime.now()
        cnt_time = now.strftime("%H:%M:%S")
        msg_box = messagebox.askyesno(title='디아블로 런처', message='이슈를 제보할 경우 터미널에 출력된 전체 로그와 경고창, 프로그램 화면 등을 첨부하여 주세요. 만약 가능하다면 어떠한 이유로 문제가 발생하였으며, 문제가 재현 가능한지 등을 첨부하여 주시면 좀 더 빠른 대응이 가능합니다. 지금 이슈 제보 페이지를 방문하시겠습니까?')
        if msg_box:
            logformat(errorLevel.INFO, f"=== Generated Report at {cnt_time} ===")
            logformat(errorLevel.INFO, f"Current agent: {platform.system()} {platform.release()}, Python {platform.python_version()}, {check_terminal_output('git --version')}")
            if resolutionProgram:
                logformat(errorLevel.INFO, f"QRes version: {check_terminal_output('QRes /S | findstr QRes')}")
                logformat(errorLevel.INFO, f"Resolution vector: {f'{originX}x{originY} - {alteredX}x{alteredY}'}")
            else:
                logformat(errorLevel.INFO, "QRes version: None")

            if diablo2Path is not None and diablo3Path is not None and diablo4Path is not None:
                logformat(errorLevel.INFO, "Installed Diablo version: II, III, IV")
                logformat(errorLevel.INFO, f"Diablo II Resurrected mods: {definedMod if definedMod is not None else 'N/A'}")
            elif diablo2Path is not None or diablo3Path is not None or diablo4Path is not None:
                logformat(errorLevel.INFO, "Installed Diablo version: partially")
                logformat(errorLevel.INFO, f"Diablo II Resurrected mods: {definedMod if definedMod is not None else 'N/A'}")
            else:
                logformat(errorLevel.INFO, "Installed Diablo version: None")

            logformat(errorLevel.INFO, f"Diablo Executed: {'True' if diabloExecuted else 'False'}")
            logformat(errorLevel.INFO, "===== End Report ======")
            logformat(errorLevel.WARN, 'NOTE: Please attach the terminal output after the code-page log')
            webbrowser.open('https://github.com/HyeongminKim/DiabloLauncher/issues')

    def AboutThisApp(*args):
        about = Tk()
        about.title("이 디아블로 런처에 관하여")
        about.geometry(f"480x310+{int(root.winfo_x() + root.winfo_reqwidth() / 2 - 480 / 2)}+{int(root.winfo_y() + root.winfo_reqheight() / 2 - 310 / 2)}")
        about.deiconify()
        about.resizable(False, False)
        about.attributes('-toolwindow', True)
        about.attributes('-topmost', 'true')

        def openBlizzardLegalSite():
            webbrowser.open('https://www.blizzard.com/en-us/legal/9c9cb70b-d1ed-4e17-998a-16c6df46be7b/copyright-notices')
        def openAppleLegalSite():
            webbrowser.open('https://www.apple.com/kr/legal/intellectual-property/guidelinesfor3rdparties.html')

        def OpenDevSite():
            webbrowser.open('https://github.com/HyeongminKim/DiabloLauncher')

        if resolutionProgram and releaseMode:
            logformat(errorLevel.INFO, "Resolution change program detected. Checking QRes version and license")
            text = Label(about, text=f"{platform.system()} {platform.release()}\n\n--- Copyright ---\nDiablo II Resurrected, Diablo III, Diablo IV\n(c) 2022 BLIZZARD ENTERTAINMENT, INC. ALL RIGHTS RESERVED.\n\nDiablo Launcher [Executable]\nCopyright (c) 2022-2023 Hyeongmin Kim\n\n{check_terminal_output('QRes /S | findstr QRes')}\n{check_terminal_output('QRes /S | findstr Copyright')}\n\n이 디아블로 런처에서 언급된 특정 상표는 각 소유권자들의 자산입니다.\n디아블로(Diablo), 블리자드(Blizzard)는 Blizzard Entertainment, Inc.의 등록 상표입니다.\nBootCamp, macOS는 Apple, Inc.의 등록 상표입니다.\n\n자세한 사항은 아래 버튼을 클릭해 주세요\n")
        elif not resolutionProgram and releaseMode:
            logformat(errorLevel.INFO, "Resolution change program does not detected")
            text = Label(about, text=f"{platform.system()} {platform.release()}\n\n--- Copyright ---\nDiablo II Resurrected, Diablo III, Diablo IV\n(c) 2022 BLIZZARD ENTERTAINMENT, INC. ALL RIGHTS RESERVED.\n\nDiablo Launcher [Executable]\nCopyright (c) 2022-2023 Hyeongmin Kim\n\nQRes\nCopyright (C) Anders Kjersem.\n\n이 디아블로 런처에서 언급된 특정 상표는 각 소유권자들의 자산입니다.\n디아블로(Diablo), 블리자드(Blizzard)는 Blizzard Entertainment, Inc.의 등록 상표입니다.\nBootCamp, macOS는 Apple, Inc.의 등록 상표입니다.\n\n자세한 사항은 아래 버튼을 클릭해 주세요\n")
        elif resolutionProgram and not releaseMode:
            logformat(errorLevel.INFO, "Resolution change program detected. Checking QRes version and license")
            text = Label(about, text=f"{platform.system()} {platform.release()}, Python {platform.python_version()}, {check_terminal_output('git --version')}\n\n--- Copyright ---\nDiablo II Resurrected, Diablo III, Diablo IV\n(c) 2022 BLIZZARD ENTERTAINMENT, INC. ALL RIGHTS RESERVED.\n\nDiablo Launcher (rev: {check_terminal_output('git rev-parse --short HEAD')}, RD: {check_terminal_output('git log -1 --date=format:%Y-%m-%d --format=%ad')}, CH: {os.popen('git branch --show-current').read().strip()})\nCopyright (c) 2022-2023 Hyeongmin Kim\n\n{check_terminal_output('QRes /S | findstr QRes')}\n{check_terminal_output('QRes /S | findstr Copyright')}\n\n이 디아블로 런처에서 언급된 특정 상표는 각 소유권자들의 자산입니다.\n디아블로(Diablo), 블리자드(Blizzard)는 Blizzard Entertainment, Inc.의 등록 상표입니다.\nBootCamp, macOS는 Apple, Inc.의 등록 상표입니다.\n\n자세한 사항은 아래 버튼을 클릭해 주세요\n")
        elif not resolutionProgram and not releaseMode:
            logformat(errorLevel.INFO, "Resolution change program does not detected")
            text = Label(about, text=f"{platform.system()} {platform.release()}, Python {platform.python_version()}, {check_terminal_output('git --version')}\n\n--- Copyright ---\nDiablo II Resurrected, Diablo III, Diablo IV\n(c) 2022 BLIZZARD ENTERTAINMENT, INC. ALL RIGHTS RESERVED.\n\nDiablo Launcher (rev: {check_terminal_output('git rev-parse --short HEAD')}, RD: {check_terminal_output('git log -1 --date=format:%Y-%m-%d --format=%ad')}, CH: {os.popen('git branch --show-current').read().strip()})\nCopyright (c) 2022-2023 Hyeongmin Kim\n\nQRes\nCopyright (C) Anders Kjersem.\n\n이 디아블로 런처에서 언급된 특정 상표는 각 소유권자들의 자산입니다.\n디아블로(Diablo), 블리자드(Blizzard)는 Blizzard Entertainment, Inc.의 등록 상표입니다.\nBootCamp, macOS는 Apple, Inc.의 등록 상표입니다.\n\n자세한 사항은 아래 버튼을 클릭해 주세요\n")

        blizzard = Button(about, text='블리자드 라이선스', command=openBlizzardLegalSite)
        apple = Button(about, text='애플 라이선스', command=openAppleLegalSite)
        this_app = Button(about, text='디아블로 런처 라이선스', command=OpenDevSite)

        text.grid(row=0, column=0, columnspan=3)
        blizzard.grid(row=1, column=0)
        this_app.grid(row=1, column=1)
        apple.grid(row=1, column=2)

        if(CheckDarkMode()):
            about['background'] = '#272727'
            text['background'] = '#272727'
            text['foreground'] = '#FFFFFF'
            blizzard['background'] = '#272727'
            blizzard['activebackground'] = '#272727'
            blizzard['foreground'] = '#FFFFFF'
            blizzard['activeforeground'] = '#FFFFFF'
            apple['background'] = '#272727'
            apple['activebackground'] = '#272727'
            apple['foreground'] = '#FFFFFF'
            apple['activeforeground'] = '#FFFFFF'
            this_app['background'] = '#272727'
            this_app['activebackground'] = '#272727'
            this_app['foreground'] = '#FFFFFF'
            this_app['activeforeground'] = '#FFFFFF'
        else:
            about['background'] = '#F0F0F0'
            text['background'] = '#F0F0F0'
            text['foreground'] = '#000000'
            blizzard['background'] = '#F0F0F0'
            blizzard['activebackground'] = '#F0F0F0'
            blizzard['foreground'] = '#000000'
            blizzard['activeforeground'] = '#000000'
            apple['background'] = '#F0F0F0'
            apple['activebackground'] = '#F0F0F0'
            apple['foreground'] = '#000000'
            apple['activeforeground'] = '#000000'
            this_app['background'] = '#F0F0F0'
            this_app['activebackground'] = '#F0F0F0'
            this_app['foreground'] = '#000000'
            this_app['activeforeground'] = '#000000'
        about.mainloop()

    def BootCampSoundRecover():
        msg_box = messagebox.askyesno(title='디아블로 런처', message='"사운드 장치 문제해결" 메뉴는 사운드 장치가 Cirrus Logic일 경우에만 적용됩니다. 계속하시겠습니까?')
        if msg_box:
            soundRecover = Tk()
            soundRecover.title("Cirrus Logic 문제 해결")
            soundRecover.geometry(f"480x170+{int(root.winfo_x() + root.winfo_reqwidth() / 2 - 480 / 2)}+{int(root.winfo_y() + root.winfo_reqheight() / 2 - 170 / 2)}")
            soundRecover.deiconify()
            soundRecover.resizable(False, False)
            soundRecover.attributes('-toolwindow', True)
            soundRecover.attributes('-topmost', 'true')
            notice = Label(soundRecover, text='이 도움말의 일부 과정은 macOS의 BootCamp 지원 앱에서 수행해야 합니다.')
            contents = Label(soundRecover, text='1. BootCamp 지원 앱에서 Windows 지원 소프트웨어를 USB에 저장합니다.\n2. BootCamp로 재시동합니다.\n3. msconfig를 실행에 입력하여 부팅 옵션을 안전 부팅의 최소 설치로 선택합니다.\n4. BootCamp를 안전모드로 재시동합니다. \n5. 실행에 devmgmt.msc를 입력하여 장치관리자를 띄웁니다. \n6. Cirrus Logic 디바이스와 드라이버를 제거합니다.\n7. 1번에서 다운받은 폴더 경로를 드라이버 설치경로로 선택합니다. \n8. msconfig를 실행에 입력하여 안전부팅 체크박스를 해제합니다. \n9. BootCamp를 재시동합니다. ', anchor=W, justify=LEFT)
            notice.pack()
            contents.pack()

            if(CheckDarkMode()):
                soundRecover['background'] = '#272727'
                notice['background'] = '#272727'
                notice['foreground'] = '#FFFFFF'
                contents['background'] = '#272727'
                contents['foreground'] = '#FFFFFF'
            else:
                soundRecover['background'] = '#F0F0F0'
                notice['background'] = '#F0F0F0'
                notice['foreground'] = '#000000'
                contents['background'] = '#F0F0F0'
                contents['foreground'] = '#000000'
            soundRecover.mainloop()

    def OpenD2RModDir():
        if diablo2Path is not None:
            logformat(errorLevel.INFO, f'The {diablo2Path}/mods directory exist. The target directory will now open.')
            os.startfile(f'"{diablo2Path}/mods"')

    def OpenProgramDir():
        os.startfile(f"{check_terminal_output('echo %cd%')}")

    def ModApplyHelp():
        logformat(errorLevel.INFO, 'Unable to load mods detail. no such file or directory.')
        messagebox.showinfo(title='디아블로 모드', message='Diablo II Resurrected에 모드를 적용하기 위해서 명령행 인수에 " -mod 모드명 -txt"를 입력해야 합니다.')
        ShowWindow()

    def ModAutoApply():
        if diabloExecuted or check_terminal_output('tasklist | findstr "Battle.net.exe" > NUL 2>&1', True) is not None:
            logformat(errorLevel.ERR, "Unable to open mods helper. reason: Battle.net or Diablo is now running.")
            messagebox.showerror(title='디아블로 모드', message='현재 디아블로 또는 Battle.net이 실행 중입니다. 예기치 않은 오류를 최소화하기 위해 먼저 해당 앱을 종료한 후 다시 시도해 주세요.')
            ShowWindow()
            return

        external_conf = loadConfigurationFile()
        if definedMod is not None and external_conf != f' -mod {definedMod} -txt':
            if(dumpConfigurationFile(f' -mod {definedMod} -txt')):
                logformat(errorLevel.INFO, f'Successfully applied mods name: " -mod {definedMod} -txt" in {userApp}/Battle.net/Battle.net.config.')
                applyHelp['text'] = f'{definedMod} 모드\n적용해제'
                GetModDetails()
                FindGameInstalled()
            else:
                logformat(errorLevel.ERR, f'Unable to load mods name: " -mod {definedMod} -txt" in {userApp}/Battle.net/Battle.net.config.')
                messagebox.showinfo(title='디아블로 모드', message=f'Diablo II Resurrected에 모드를 적용하기 위해서 명령행 인수에 " -mod {definedMod} -txt"를 입력해야 합니다.')
                ShowWindow()
        elif definedMod is not None and external_conf == f' -mod {definedMod} -txt':
            if(dumpConfigurationFile('')):
                logformat(errorLevel.INFO, f'Successfully unloaded mods name: " -mod {definedMod} -txt" in {userApp}/Battle.net/Battle.net.config.')
                applyHelp['text'] = f'{definedMod} 모드\n적용하기'
                GetModDetails()
                FindGameInstalled()
            else:
                logformat(errorLevel.ERR, f'Unable to unload mods name: " -mod {definedMod} -txt" in {userApp}/Battle.net/Battle.net.config.')
                messagebox.showinfo(title='디아블로 모드', message=f'Diablo II Resurrected를 모드 없이 플레이하기 위해서 명령행 인수에 " -mod {definedMod} -txt"를 제거해야 합니다.')
                ShowWindow()

    def ModGeneralHelp():
        messagebox.showinfo(title='디아블로 모드', message='"없는 문자열" 오류가 발생할 경우 모드팩 업데이트가 출시 되었는지 확인하시거나, json파일의 모든 누락된 ID를 직접 추가해 주세요. 자세한 사항은 "모드 업데이트 방법"을 참조해 주세요')
        ShowWindow()

    def ModAdvancedHelp():
        msg_box = messagebox.askyesno(title='디아블로 모드', message='Diablo II Resurrected 모드 생성 또는 편집시 유용한 프로그램 리스트를 확인하시겠습니까?')
        if msg_box:
            webbrowser.open('https://github.com/eezstreet/D2RModding-SpriteEdit')
            webbrowser.open('http://www.zezula.net/en/casc/main.html')
            webbrowser.open('https://github.com/Cjreek/D2ExcelPlus')
            webbrowser.open('https://github.com/WinMerge/winmerge')
            webbrowser.open('https://github.com/microsoft/vscode')
        ShowWindow()

    def ModHelpWindow():
        global applyHelp
        envModState = loadSettings(parentLocation.UserLocalAppData, ["ModsManager", "IgnoreModsMergeDialog"])
        envMod = loadSettings(parentLocation.UserLocalAppData, ["ModsManager", "PreferMods"])

        launch.title('모드 도움말')
        note = Label(launch, text='사용가능한 도움말', height=2)
        external_conf = loadConfigurationFile()
        if definedMod is not None and isinstance(definedMod, str):
            if external_conf is not None and external_conf == f' -mod {definedMod} -txt':
                applyHelp = Button(launch, text=f'{definedMod} 모드\n적용해제', width=20, height=5, command=ModAutoApply, state='normal')
            else:
                applyHelp = Button(launch, text=f'{definedMod} 모드\n적용하기', width=20, height=5, command=ModAutoApply, state='normal')
        elif definedMod is None or definedMod == "" or (envModState is not None and envModState is True):
            applyHelp = Button(launch, text='모드\n적용방법', width=20, height=5, command=ModApplyHelp, state='normal')
        else:
            applyHelp = Button(launch, text='모드\n병합필요', width=20, height=5, command=ModApplyHelp, state='disabled')

        if definedMod is not None and definedMod != "" and envModState is None or envModState is False:
            if isinstance(definedMod, str):
                logformat(errorLevel.INFO, 'mods resolve problem button was enabled.')
                generalHelp = Button(launch, text=f'{definedMod} 모드\n문제해결', width=20, height=2, command=ModGeneralHelp, state='normal')
            else:
                logformat(errorLevel.INFO, 'mods resolve problem button was disabled. reason: Too many loads mod details.')
                generalHelp = Button(launch, text='모드 문제해결', width=20, height=2, command=ModGeneralHelp, state='disabled')

            advancedHelp = Button(launch, text='모드 업데이트 방법', width=20, height=2, command=ModAdvancedHelp, state='normal')
        else:
            logformat(errorLevel.INFO, 'mods resolve problem button was disabled. reason: Unable to load mods detail. no such file or directory.')
            generalHelp = Button(launch, text='모드 문제해결', width=20, height=3, command=ModGeneralHelp, state='disabled')
            advancedHelp = Button(launch, text='새로운 모드 생성', width=20, height=2, command=ModAdvancedHelp, state='normal')

        note.grid(row=0, column=0, columnspan=2)
        generalHelp.grid(row=1, column=0)
        advancedHelp.grid(row=2, column=0)
        applyHelp.grid(row=1, column=1, rowspan=3)

        if(CheckDarkMode()):
            note['background'] = '#272727'
            note['foreground'] = '#FFFFFF'
            generalHelp['background'] = '#272727'
            generalHelp['activebackground'] = '#272727'
            generalHelp['foreground'] = '#FFFFFF'
            generalHelp['activeforeground'] = '#FFFFFF'
            advancedHelp['background'] = '#272727'
            advancedHelp['activebackground'] = '#272727'
            advancedHelp['foreground'] = '#FFFFFF'
            advancedHelp['activeforeground'] = '#FFFFFF'
            applyHelp['background'] = '#272727'
            applyHelp['activebackground'] = '#272727'
            applyHelp['foreground'] = '#FFFFFF'
            applyHelp['activeforeground'] = '#FFFFFF'
        else:
            note['background'] = '#F0F0F0'
            note['foreground'] = '#000000'
            generalHelp['background'] = '#F0F0F0'
            generalHelp['activebackground'] = '#F0F0F0'
            generalHelp['foreground'] = '#000000'
            generalHelp['activeforeground'] = '#000000'
            advancedHelp['background'] = '#F0F0F0'
            advancedHelp['activebackground'] = '#F0F0F0'
            advancedHelp['foreground'] = '#000000'
            advancedHelp['activeforeground'] = '#000000'
            applyHelp['background'] = '#F0F0F0'
            applyHelp['activebackground'] = '#F0F0F0'
            applyHelp['foreground'] = '#000000'
            applyHelp['activeforeground'] = '#000000'

        ShowWindow()
        launch.mainloop()

    def FlushBattleNetCache():
        result = check_terminal_output('tasklist | findstr "Battle.net.exe > NUL 2>&1', True)
        if result is None:
            dialog = messagebox.askyesno('디아블로 런처', 'Battle.net 로그인이 해제될 수 있으며 설정이 초기화 될 수 있습니다. Battle.net 캐시는 영구적으로 삭제되며 되돌릴 수 없습니다. 계속하시겠습니까?')
            if not dialog: return

            if call(f'rmdir /s /q "{userApp}\\Battle.net" > NUL 2>&1', shell=True) != 0 or call(f'rmdir /s /q "{userLocalApp}\\Battle.net" > NUL 2>&1', shell=True) != 0 or call(f'rmdir /s /q "{userLocalApp}\\Blizzard Entertainment" > NUL 2>&1', shell=True) != 0:
                messagebox.showerror('디아블로 런처', 'Battle.net 캐시가 완전히 제거되지 않았습니다. 디렉터리가 존재하지 않거나 쓰기 권한이 없을 경우 해당 문제가 발생할 수 있습니다.')
        else:
            messagebox.showerror('디아블로 런처', 'Battle.net 캐시를 제거할 수 없습니다. Battle.net을 종료한 후 다시 시도해 주세요.')
        FindGameInstalled()

    menubar = Menu(root)
    fileMenu = Menu(menubar, tearoff=0)

    fileMenu.add_command(label='Battle.net 실행', command=OpenBattleNet, state='disabled', accelerator='Ctrl+O')
    fileMenu.add_command(label='Battle.net 캐시 제거...', command=FlushBattleNetCache, state='disabled')
    fileMenu.add_separator()
    fileMenu.add_command(label='디아블로 런처 종료', command=ExitProgram, accelerator='Ctrl+W')

    menubar.add_cascade(label='파일', menu=fileMenu)

    toolsMenu = Menu(menubar, tearoff=0)
    toolsMenu.add_command(label='새로 고침', command=ForceReload, accelerator='F5')
    toolsMenu.add_command(label='런처 업데이트 확인...', command=UpdateProgram)
    toolsMenu.add_separator()
    toolsMenu.add_command(label='디아블로 런처 설정', state='disabled', command=SetLauncherConfigurationValues, accelerator='Ctrl+,')

    if os.path.isfile('C:/Program Files/Boot Camp/Bootcamp.exe'):
        toolsMenu.add_command(label='소리 문제 해결...', command=BootCampSoundRecover, state='normal')
    else:
        toolsMenu.add_command(label='소리 문제 해결...', command=BootCampSoundRecover, state='disabled')

    toolsMenu.add_separator()
    toolsMenu.add_command(label='프로그램 제거 및 변경', command=openControlPanel)
    toolsMenu.add_command(label='통계 재설정...', command=ResetGameStatus)
    menubar.add_cascade(label='도구', menu=toolsMenu)

    modMenu = Menu(menubar, tearoff=0)
    modMenu.add_command(label='D2R 모드 디렉토리 열기', state='disabled', command=OpenD2RModDir)
    modMenu.add_command(label='현재 모드: 알 수 없음', state='disabled')
    modMenu.add_separator()
    modMenu.add_command(label='모드 도움말...', command=ModHelpWindow)
    menubar.add_cascade(label='모드', menu=modMenu)

    aboutMenu = Menu(menubar, tearoff=0)
    aboutMenu.add_command(label='이 디아블로 런처에 관하여...', command=AboutThisApp, accelerator='F1')
    aboutMenu.add_separator()

    gameMenu = Menu(aboutMenu, tearoff=0)
    gameMenu.add_command(label='D2R 디렉토리 열기', command=OpenD2RDir, state='disabled')
    gameMenu.add_command(label='Diablo III 디렉토리 열기', command=OpenD3Dir, state='disabled')
    gameMenu.add_command(label='Diablo IV 디렉토리 열기', command=OpenD4Dir, state='disabled')

    aboutMenu.add_cascade(label='게임 디렉토리', menu=gameMenu)
    aboutMenu.add_command(label='통계 디렉토리 열기', command=OpenGameStatusDir, state='disabled')
    aboutMenu.add_command(label='디아블로 런처 디렉토리 열기', command=OpenProgramDir)
    aboutMenu.add_separator()

    logLevel = loadSettings(parentLocation.UserLocalAppData, ["General", "LoggingInfoLevel"])
    if logLevel is not None and logLevel is True and not releaseMode:
        aboutMenu.add_command(label='버그 신고...', command=OpenDevIssues, state='normal', accelerator='F12')
    else:
        aboutMenu.add_command(label='버그 신고...', command=OpenDevIssues, state='disabled', accelerator='F12')

    menubar.add_cascade(label='정보', menu=aboutMenu)

    root.bind_all("<F5>", ForceReload)
    root.bind_all("<F1>", AboutThisApp)
    root.bind_all("<F12>", OpenDevIssues)
    root.bind_all("<Control-w>", ExitProgram)
    root.bind_all("<Control-o>", OpenBattleNet)
    root.bind_all("<Control-,>", SetLauncherConfigurationValues)

    welcome = Label(root, text='')
    switchButton = Button(rootFrame, text='디아블로 실행...', command=LaunchGameAgent, width=35, height=5, state='disabled')
    emergencyButton = Button(rootFrame, text='긴급 전원 작업\n(게임 저장 후 실행 요망)', width=35, height=5, command=EmgergencyReboot)

    switchButton.grid(column=0, row=0)
    emergencyButton.grid(column=1, row=0)

    now = datetime.now()
    cnt_time = now.strftime("%H:%M:%S")

    FindGameInstalled()
    GetLauncherConfigurationValues()
    RequirementCheck()

    if resolutionProgram:
        status = Label(root, text=f"\n정보 - {cnt_time}에 업데이트\n해상도 변경 지원됨: 예\n해상도 벡터: {f'{originX}x{originY} - {alteredX}x{alteredY}'}\n현재 해상도: {f'{alteredX}x{alteredY} {alteredFR}Hz' if diabloExecuted else f'{originX}x{originY} {originFR}Hz'}\n디아블로 실행: {'예' if diabloExecuted else '아니요'}\n")
    else:
        status = Label(root, text=f"\n정보 - {cnt_time}에 업데이트\n해상도 변경 지원됨: 아니요\n\n\n디아블로 실행: {'예' if diabloExecuted else '아니요'}\n")

    if os.path.isfile('C:/Program Files/Boot Camp/Bootcamp.exe'):
        info = Label(root, text='도움말\n디아블로를 원할히 플레이하려면 DiabloLauncher 환경 변수를 설정해 주세요.\n게임 디렉토리, 해상도를 변경하려면 DiabloLauncher 환경변수를 편집하세요.\nBootCamp 사운드 장치가 작동하지 않을 경우 소리 문제 해결 메뉴를 확인해 보세요.')
    else:
        info = Label(root, text='도움말\n디아블로를 원할히 플레이하려면 DiabloLauncher 환경 변수를 설정해 주세요.\n게임 디렉토리, 해상도를 변경하려면 DiabloLauncher 환경변수를 편집하세요.\n디아블로를 실행하기 전 사운드 장치가 제대로 설정 되어있는지 확인해 보세요.')
    notice = Label(root, text="Blizzard 정책상 게임 실행은 직접 실행하여야 하며 실행시 알림창 지시를 따르시기 바랍니다.\n해당 프로그램을 사용함으로써 발생하는 모든 불이익은 전적으로 사용자에게 있습니다.\n지원되는 디아블로 버전은 Diablo II Resurrected, Diablo III, Diablo IV 입니다.")

    statusbar = Label(root, text='Initializing...', bd=1, relief='sunken')

    welcome.pack()
    rootFrame.pack()
    status.pack()
    info.pack()
    notice.pack()
    statusbar.pack(side=BOTTOM, fill='x')

    ReloadStatusBar()
    CheckDarkMode()

    root.config(menu=menubar)

    root.mainloop()

if __name__ == '__main__':
    releaseMode = not os.path.isdir(f"{check_terminal_output('echo %cd%')}/.git")
    if not releaseMode:
        logLevel = loadSettings(parentLocation.UserLocalAppData, ["General", "LoggingInfoLevel"])
        if logLevel is not None and logLevel is True:
            os.environ['LOG_VERBOSE_LEVEL'] = 'verbose'
            multiprocessing.log_to_stderr()
            logger = multiprocessing.get_logger()
            logger.setLevel(logging.INFO)

        mainThread = multiprocessing.Process(target=init)
        updateThread = multiprocessing.Process(target=UpdateProgram)

        mainThread.start()
        updateThread.start()

        mainThread.join()
        updateThread.join()
    else:
        init()
