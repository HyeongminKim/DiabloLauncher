#-*- coding:utf-8 -*-

# pylint: disable=W0104,W0603,W0621
# pylint: disable=C0200,C0302,C0415,R1722,C0115,C0116

try:
    import os
    os.system('')
    f'[FATL: 70-01-01 12:00] The DiabloLauncher stopped due to unsupported python version. (version_info < {3})'

    import subprocess
    from src.utility.logcat import logformat, errorLevel, color
    from src.utility.terminal import check_terminal_output
except (ModuleNotFoundError, ImportError) as error:
    print(f'\033[35m[FATL: 70-01-01 12:00] The DiabloLauncher stopped due to {error}\033[0m')
    exit(1)

userApp = os.environ.get('AppData')
userLocalApp = os.environ.get('LocalAppData')

try:
    import platform
    if platform.system() != 'Windows':
        raise OSError(f'{platform.system()} system does not support yet.')

    os.system('chcp 65001 > NUL')
    logformat(errorLevel.INFO, 'Active code page: UTF-8 (0xfde9)')

    if platform.release() == '7' or platform.release() == '8' or platform.release() == '10' or platform.release() == '11':
        logformat(errorLevel.INFO, 'support OS detected.')
    else:
        logformat(errorLevel.FATL, f'{platform.system()} {platform.release()} does not support. Please check Diablo Requirements and Specifications.')

    import multiprocessing
    import sys
    import webbrowser

    if multiprocessing.cpu_count() >= 2 and sys.maxsize > 2**32:
        logformat(errorLevel.INFO, f'supported {platform.processor()} CPU detected. creating GUI...')
    else:
        logformat(errorLevel.FATL, f"{platform.processor()} CPU does not support (core: {multiprocessing.cpu_count()}, {'x64' if sys.maxsize > 2**32 else 'x86'}).\n\tPlease check Diablo Requirements and Specifications.")

    import signal
    import logging

    from datetime import datetime
    import time

    from tkinter import Tk
    from tkinter import Label
    from tkinter import Button
    from tkinter import (LEFT, RIGHT, BOTTOM)
    from tkinter import (W, CENTER)
    from tkinter import Menu
    from tkinter import messagebox
    from tkinter import Entry
    from tkinter import Frame
    from idlelib.tooltip import Hovertip

    from src.data.registry import ReturnRegistryQuery, OpenProgramUsingRegistry, TestRegistryValue
    from src.data.game_data import FormatTime, SaveGameRunningTime, ClearGameRunningTime, ignoreTime
except (ModuleNotFoundError, ImportError, OSError) as error:
    print(f'\033[35m[FATL: 70-01-01 12:00] The DiabloLauncher stopped due to {error}\033[0m')
    exit(1)

diabloExecuted = False
updateChecked = False
forceReboot = False

rebootWaitTime = 10
loadWaitTime = 10

gameStartTime = None
gameEndTime = None

envData = None
diablo2Path = None
diablo3Path = None
diablo4Path = None

definedMod = None
resolutionProgram = False

originX = None
originY = None
originFR = None
alteredX = None
alteredY = None
alteredFR = None

root = Tk()
root.withdraw()
launch = Tk()
launch.withdraw()

switchButton = None
emergencyButton = None
status = None
statusbar = None

fileMenu = None
toolsMenu = None
aboutMenu = None
modMenu = None

def ShowWindow():
    launch.deiconify()
    launch.after(1, launch.focus_force())

def HideWindow():
    root.after(1, root.focus_force())
    for widget in launch.winfo_children():
        logformat(errorLevel.INFO, f'abandoning module {widget}')
        widget.destroy()
    launch.title('무제')
    launch.withdraw()

def CheckResProgram():
    global resolutionProgram
    logformat(errorLevel.INFO, 'QRes install check')
    if os.path.isfile('C:/Windows/System32/Qres.exe') or os.path.isfile(f'{userLocalApp}/Programs/Common/QRes.exe'):
        if os.path.isfile(f'{userLocalApp}/Programs/Common/QRes.exe') and os.system('where QRes > NUL 2>&1') != 0:
            logformat(errorLevel.ERR, f"QRes installed in {userLocalApp}/Programs/Common/QRes.exe. However that program will not discovered in future operation. Please add environment variable to fix this issue.")
            toolsMenu.entryconfig(3, state='disabled')
            resolutionProgram = False
        else:
            logformat(errorLevel.INFO, f"QRes installed in {check_terminal_output('where QRes')}")
            toolsMenu.entryconfig(3, state='normal')
            resolutionProgram = True
    else:
        logformat(errorLevel.INFO, 'QRes did not installed')
        toolsMenu.entryconfig(3, state='disabled')
        resolutionProgram = False

def AlertWindow():
    msg_box = messagebox.askquestion('디아블로 런처', f'현재 디스플레이 해상도가 {alteredX}x{alteredY} 로 조정되어 있습니다. 게임이 실행 중인 상태에서 해상도 설정을 복구할 경우 퍼포먼스에 영향을 미칠 수 있습니다. 그래도 해상도 설정을 복구하시겠습니까?', icon='question')
    if msg_box == 'yes':
        LaunchGameAgent()
        ExitProgram()
    else:
        messagebox.showwarning('디아블로 런처', '해상도가 조절된 상태에서는 런처를 종료할 수 없습니다. 먼저 해상도를 기본 설정으로 변경해 주시기 바랍니다.')

def ExitProgram():
    if(launch is not None and root is not None):
        for widget in launch.winfo_children():
            logformat(errorLevel.INFO, f'Shutting down and abandoning module {widget}')
            widget.destroy()
        launch.destroy()

        for widget in root.winfo_children():
            logformat(errorLevel.INFO, f'Shutting down and abandoning module {widget}')
            widget.destroy()
        root.destroy()
    exit(0)

def InterruptProgram(sig, frame):
    logformat(errorLevel.ERR, f'Keyboard Interrupt: {sig}')
    if diabloExecuted:
        LaunchGameAgent()
    ExitProgram()

def UpdateProgram():
    global updateChecked

    if os.system('where git > NUL 2>&1') == 0:
        localCommit = os.popen('git rev-parse HEAD').read().strip()
        localVersion = os.popen('git rev-parse --short HEAD').read().strip()
        logformat(errorLevel.INFO, 'Checking program updates...')
        if os.system('git pull --rebase origin master > NUL 2>&1') == 0:
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
        elif os.system('ping -n 1 -w 1 www.google.com > NUL 2>&1') != 0:
            messagebox.showwarning('디아블로 런처', '인터넷 연결이 오프라인인 상태에서는 디아블로 런처를 업데이트 할 수 없습니다. 나중에 다시 시도해 주세요.')
            logformat(errorLevel.ERR, 'Program update failed. Please check your internet connection.')
        else:
            os.system('git status')
            messagebox.showwarning('디아블로 런처', '레포에 알 수 없는 오류가 발생하였습니다. 자세한 사항은 로그를 참조해 주세요. ')
            logformat(errorLevel.ERR, 'Program update failed. Please see the output.')
        updateChecked = True
    elif os.system('where git > NUL 2>&1') != 0 and updateChecked:
        logformat(errorLevel.INFO, 'git command does not currently installed. downloading master.zip')
        webbrowser.open('https://github.com/HyeongminKim/DiabloLauncher/archive/refs/heads/master.zip')
        messagebox.showwarning('디아블로 런처', 'Git이 시스템에 설치되어 있지 않아 자동 업데이트를 사용할 수 없습니다. 다운로드 된 master.zip 파일 압축을 풀어 설치된 경로에 덮어쓰기해 주세요.')
    elif os.system('where git > NUL 2>&1') != 0 and not updateChecked:
        logformat(errorLevel.WARN, 'Automatically checking for updates has been disabled. Run the updater function again to switch to legacy update mode. ')
        updateChecked = True

def LoadGameRunningTime():
    data = []
    stat_max = 0
    stat_sum = 0
    runtimeFile = None
    try:
        if os.path.isfile(f'{userApp}/DiabloLauncher/runtime.log'):
            runtimeFile = open(f'{userApp}/DiabloLauncher/runtime.log', 'r', encoding='utf-8')
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
            fileMenu.entryconfig(3, state='normal')
        else:
            raise FileNotFoundError
    except (OSError, FileNotFoundError) as error:
        logformat(errorLevel.ERR, f'Failed to load Game-play logs: {error}')
        if os.path.isdir(f'{userApp}/DiabloLauncher'):
            fileMenu.entryconfig(3, state='normal')
        else:
            fileMenu.entryconfig(3, state='disabled')
        return 0, 0, 0, 0
    else:
        if runtimeFile is not None:
            runtimeFile.close()
        if data is not None and stat_sum != 0:
            return len(data), stat_max, stat_sum, (stat_sum / len(data))
        elif data is not None and stat_sum == 0:
            return len(data), stat_max, 0, 0
        else:
            return 0, 0, 0, 0

def GameLauncher(gameName: str, supportedX: int, supportedY: int, os_min: int):
    global diabloExecuted
    global gameStartTime
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
        if os.system(f'QRes /L | findstr /r "{alteredX}x" |findstr /r "{alteredY}," | findstr /r "\\<{alteredFR}\\>" > NUL 2>&1') != 0:
            logformat(errorLevel.ERR, f'The current display does not supported choosed resolution {alteredX}x{alteredY} {alteredFR}Hz')
            messagebox.showwarning('디아블로 런처', f'{alteredX}x{alteredY} {alteredFR}Hz 해상도는 이 디스플레이에서 지원하지 않습니다. 시스템 환경 설정에서 지원하는 해상도를 확인하시기 바랍니다.')
            diabloExecuted = False
            root.protocol("WM_DELETE_WINDOW", ExitProgram)
            HideWindow()
            UpdateStatusValue()
            ReloadStatusBar()
            return

        os.system(f'QRes -X {alteredX} -Y {alteredY} -R {alteredFR} > NUL 2>&1')
        switchButton['text'] = '디스플레이 해상도 복구\n(게임 종료시 사용)'
        root.protocol("WM_DELETE_WINDOW", AlertWindow)
    else:
        switchButton['text'] = '게임 종료'
    if(gameName == 'Diablo II Resurrected'):
        os.popen(f'"{diablo2Path}/{gameName} Launcher.exe"')
    elif(gameName == 'Diablo III'):
        os.popen(f'"{diablo3Path}/{gameName} Launcher.exe"')
    elif(gameName == 'Diablo IV'):
        os.popen(f'"{diablo4Path}/{gameName} Launcher.exe"')
    toolsMenu.entryconfig(3, state='disabled')
    gameStartTime = time.time()
    HideWindow()
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
        if resolutionProgram:
            toolsMenu.entryconfig(3, state='normal')
            if os.system(f'QRes /L | findstr /r "{originX}x" |findstr /r "{originY}," | findstr /r "\\<{originFR}\\>" > NUL 2>&1') != 0:
                logformat(errorLevel.ERR, f'The current display does not supported choosed resolution {alteredX}x{alteredY} {alteredFR}Hz')
                messagebox.showwarning('디아블로 런처', f'{originX}x{originY} {originFR}Hz 해상도는 이 디스플레이에서 지원하지 않습니다. 시스템 환경 설정에서 지원하는 해상도를 확인하시기 바랍니다.')
            else:
                os.system(f'QRes -X {originX} -Y {originY} -R {originFR} > NUL 2>&1')

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
        diablo4 = Button(launch, text='Diablo IV 베타\n설치되지 않음', width=20, height=2, command= lambda: GameLauncher('Diablo IV', 1280, 720, 10))

        note.grid(row=0, column=0, columnspan=2)
        diablo2.grid(row=1, column=0, rowspan=2)
        diablo3.grid(row=1, column=1)
        diablo4.grid(row=2, column=1)

        if diablo2Path is None or not os.path.isfile(diablo2Path + '/Diablo II Resurrected Launcher.exe'):
            logformat(errorLevel.INFO, 'Diablo II Resurrected launch button disabled, because launcher is not detected.')
            diablo2['state'] = "disabled"
        else:
            logformat(errorLevel.INFO, 'Diablo II Resurrected launch button enabled.')
            diablo2['state'] = "normal"
            if os.path.isdir(diablo2Path + '/mods'):
                logformat(errorLevel.INFO, 'Diablo II Resurrected mods directory detected.')
                GetModDetails()
                if definedMod is not None and isinstance(definedMod, list):
                    logformat(errorLevel.WARN, "Diablo II Resurrected mods are not cached. Because too many mods detected.")
                    diablo2['text'] = 'Diablo II Resurrected\n모드병합 필요'
                elif definedMod is not None and isinstance(definedMod, str):
                    if os.path.isdir(diablo2Path + '/mods/' + definedMod + f'/{definedMod}.mpq/data') or os.path.isfile(diablo2Path + '/mods/' + definedMod + f'/{definedMod}.mpq'):
                        diablo2['text'] = f'Diablo II Resurrected\n{definedMod} 적용됨'
                    else:
                        messagebox.showwarning(title='디아블로 모드 관리자', message='유효하지 않은 모드 배치가 감지되었습니다. ')
                        logformat(errorLevel.WARN, f"The mod {definedMod} does not followed by path:")
                        logformat(errorLevel.WARN, f"\t- {diablo2Path + '/mods/' + definedMod + f'{definedMod}.mpq'}")
                        logformat(errorLevel.WARN, f"\t- {diablo2Path + '/mods/' + definedMod + f'{definedMod}.mpq/data'}")
                        diablo2['text'] = 'Diablo II Resurrected'
                else:
                    logformat(errorLevel.INFO, "Diablo II Resurrected mods are not cached. Because mods was not installed yet.")
                    diablo2['text'] = 'Diablo II Resurrected'
            else:
                logformat(errorLevel.INFO, 'Diablo II Resurrected mods directory not found.')
                diablo2['text'] = 'Diablo II Resurrected'

        if diablo3Path is None or not os.path.isfile(diablo3Path + '/Diablo III Launcher.exe'):
            logformat(errorLevel.INFO, 'Diablo III launch button disabled, because launcher is not detected.')
            diablo3['state'] = "disabled"
        else:
            logformat(errorLevel.INFO, 'Diablo III launch button enabled.')
            diablo3['state'] = "normal"
            diablo3['text'] = 'Diablo III'

        if diablo4Path is None or not os.path.isfile(diablo4Path + '/Diablo IV Launcher.exe'):
            logformat(errorLevel.INFO, 'Diablo IV launch button disabled, because launcher is not detected.')
            diablo4['state'] = "disabled"
        else:
            logformat(errorLevel.INFO, 'Diablo IV launch button enabled.')
            diablo4['state'] = "normal"
            diablo4['text'] = 'Diablo IV 베타\n3월 27일 만료 예정'

        diablo4['state'] = "disabled"
        diablo4['text'] = 'Diablo IV 베타\n3월 25일 출시 예정'

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
        if os.system(f'QRes /L | findstr /r "{originX}x" |findstr /r "{originY}," | findstr /r "\\<{originFR}\\>" > NUL 2>&1') != 0:
            logformat(errorLevel.ERR, f'The current display does not supported choosed resolution {alteredX}x{alteredY} {alteredFR}Hz')
            messagebox.showwarning('디아블로 런처', f'{originX}x{originY} {originFR}Hz 해상도는 이 디스플레이에서 지원하지 않습니다. 시스템 환경 설정에서 지원하는 해상도를 확인하시기 바랍니다.')
        else:
            os.system(f'QRes -X {originX} -Y {originY} -R {originFR} > NUL 2>&1')
    HideWindow()
    UpdateStatusValue()
    if poweroff == 'r':
        os.system('shutdown -r -f -t 10 -c "Windows가 DiabloLauncher의 [긴급 재시동] 기능으로 인해 재시동 됩니다."')
    elif poweroff == 's':
        os.system('shutdown -s -f -t 10 -c "Windows가 DiabloLauncher의 [긴급 종료] 기능으로 인해 종료 됩니다."')
    logformat(errorLevel.INFO, 'Successfully executed Windows shutdown.exe')
    statusbar['text'] = '로드할 수 없음'
    Hovertip(statusbar, text='', hover_delay=500)
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
        if resolutionProgram:
            toolsMenu.entryconfig(3, state='normal')
        os.system('shutdown -a')
        logformat(errorLevel.INFO, 'Successfully executed Windows shutdown.exe')
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
        ShowWindow()
        launch.mainloop()

def GetModDetails():
    global definedMod
    envValue = os.listdir(f'{diablo2Path}/mods')
    if isinstance(envValue, list) and len(envValue) > 1:
        logformat(errorLevel.INFO, f"Detected mods: {envValue}. checking D2R_MOD_SET env value...")
        envMod = os.environ.get('D2R_MOD_SET')
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
    msg_box = messagebox.askyesno(title='디아블로 모드', message='Diablo II Resurrected 모드를 병합하지 않고 선호하는 모드를 불러오시려면 시스템 환경변수에서 "D2R_MOD_SET" 변수에 선호하는 모드 이름을 작성하시기 바랍니다. 지금 시스템 환경변수를 설정하시겠습니까?')
    if msg_box:
        msg_box = messagebox.askyesnocancel('디아블로 런처', '시스템 또는 계정의 환경변수 편집 시 업데이트된 환경변수를 반영하기 위해 프로그램을 종료해야 합니다. 시스템 환경변수를 수정할 경우 관리자 권한이 필요합니다. 대신 사용자 환경변수를 편집하시겠습니까?', icon='question')
        if msg_box is not None and msg_box:
            logformat(errorLevel.INFO, 'starting advanced user env editor... This action will not required UAC')
            subprocess.Popen('rundll32.exe sysdm.cpl,EditEnvironmentVariables')
            messagebox.showwarning('디아블로 런처', '사용자 환경변수 수정을 모두 완료한 후 다시 실행해 주세요.')
            logformat(errorLevel.INFO, 'advanced user env editor launched. DiabloLauncher now exiting...')
            ExitProgram()
        elif msg_box is not None and not msg_box:
            logformat(errorLevel.INFO, 'starting advanced system env editor... This action will required UAC')
            os.system('sysdm.cpl ,3')
            messagebox.showwarning('디아블로 런처', '시스템 환경변수 수정을 모두 완료한 후 다시 실행해 주세요.')
            logformat(errorLevel.INFO, 'advanced system env editor launched. DiabloLauncher now exiting...')
            ExitProgram()

def FindGameInstalled():
    global diablo2Path
    global diablo3Path
    global diablo4Path

    if(TestRegistryValue(r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Diablo II Resurrected')):
        logformat(errorLevel.INFO, 'Diablo II Resurrected mod check enabled.')
        fileMenu.entryconfig(0, state='normal')
        modMenu.entryconfig(3, state='normal')

        diablo2Path = ReturnRegistryQuery(r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Diablo II Resurrected')
        if os.path.isdir(diablo2Path + '/mods'):
            modMenu.entryconfig(0, state='normal')
            modMenu.entryconfig(1, label='활성화된 모드: 검색중...')
            modMenu.entryconfig(1, state='disabled')
            logformat(errorLevel.INFO, 'Diablo II Resurrected mods directory detected.')
            GetModDetails()
            if definedMod is not None and isinstance(definedMod, list):
                logformat(errorLevel.WARN, "Diablo II Resurrected mods are not cached. Because too many mods detected.")
                modMenu.entryconfig(1, label=f'활성화된 모드: {definedMod[0]} 외 {len(definedMod) - 1}개')
                modMenu.entryconfig(1, state='normal')
                modMenu.entryconfig(1, command=ModsPreferSelector)
            elif definedMod is not None and isinstance(definedMod, str):
                if os.path.isdir(diablo2Path + '/mods/' + definedMod + f'/{definedMod}.mpq/data') or os.path.isfile(diablo2Path + '/mods/' + definedMod + f'/{definedMod}.mpq'):
                    modMenu.entryconfig(1, label=f'활성화된 모드: {definedMod}')
                    modMenu.entryconfig(1, state='normal')
                    modMenu.entryconfig(1, command=SearchModInGitHub)
                else:
                    messagebox.showwarning(title='디아블로 모드 관리자', message='유효하지 않은 모드 배치가 감지되었습니다. ')
                    logformat(errorLevel.WARN, f"The mod {definedMod} does not followed by path:")
                    logformat(errorLevel.WARN, f"\t- {diablo2Path + '/mods/' + definedMod + f'{definedMod}.mpq'}")
                    logformat(errorLevel.WARN, f"\t- {diablo2Path + '/mods/' + definedMod + f'{definedMod}.mpq/data'}")
                    modMenu.entryconfig(1, label='활성화된 모드: 검증 오류')
            else:
                logformat(errorLevel.INFO, "Diablo II Resurrected mods are not cached. Because mods was not installed yet.")
                modMenu.entryconfig(1, label='새로운 모드 탐색')
                modMenu.entryconfig(1, state='normal')
                modMenu.entryconfig(1, command=DownloadModsLink)
        else:
            logformat(errorLevel.INFO, 'Diablo II Resurrected mods directory not found.')
            modMenu.entryconfig(0, state='disabled')
            modMenu.entryconfig(1, label='새로운 모드 탐색')
            modMenu.entryconfig(1, state='normal')
            modMenu.entryconfig(1, command=DownloadModsLink)
    else:
        logformat(errorLevel.INFO, 'Diablo II Resurrected mod check disabled, because Diablo II Resurrected does not installed.')
        fileMenu.entryconfig(0, state='disabled')
        modMenu.entryconfig(0, state='disabled')
        modMenu.entryconfig(1, state='disabled')
        modMenu.entryconfig(3, state='disabled')
        modMenu.entryconfig(1, label='게임이 설치되지 않음')

    if(TestRegistryValue(r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Diablo III')):
        diablo3Path = ReturnRegistryQuery(r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Diablo III')
        fileMenu.entryconfig(1, state='normal')
    else:
        fileMenu.entryconfig(1, state='disabled')

    if(TestRegistryValue(r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Diablo IV Beta')):
        diablo4Path = ReturnRegistryQuery(r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Diablo IV Beta')
        fileMenu.entryconfig(2, state='normal')
    else:
        fileMenu.entryconfig(2, state='disabled')

    if(diablo2Path is None and diablo3Path is None and diablo4Path is None):
        switchButton['state'] = "disabled"
    else:
        switchButton['state'] = "normal"

def GetResolutionValue():
    global envData

    CheckResProgram()
    if resolutionProgram:
        global originX
        global originY
        global originFR
        global alteredX
        global alteredY
        global alteredFR

    try:
        envData = os.environ.get('DiabloLauncher')
        logformat(errorLevel.INFO, f'{envData}')
        temp = None
        if resolutionProgram:
            logformat(errorLevel.INFO, 'QRes detected. parameter count should be 6')
            originX, originY, originFR, alteredX, alteredY, alteredFR, temp = envData.split(';')
            logformat(errorLevel.INFO, 'parameter conversion succeed')
        else:
            logformat(errorLevel.INFO, 'QRes not detected. Skipping parameter conversion.')

        if resolutionProgram:
            logformat(errorLevel.INFO, f'Default resolution: {int(originX)} X {int(originY)} {float(originFR)}Hz')
            logformat(errorLevel.INFO, f'Convert resolution: {int(alteredX)} X {int(alteredY)} {float(alteredFR)}Hz')
            if (os.system(f'QRes /L | findstr /r "{originX}x" |findstr /r "{originY}," | findstr /r "\\<{originFR}\\>" > NUL 2>&1') != 0) or (os.system(f'QRes /L | findstr /r "{alteredX}x" |findstr /r "{alteredY}," | findstr /r "\\<{alteredFR}\\>" > NUL 2>&1') != 0):
                messagebox.showwarning('디아블로 런처', '일부 해상도가 이 디스플레이와 호환되지 않습니다. 시스템 환경 설정에서 지원하는 해상도를 확인하시기 바랍니다.')
                logformat(errorLevel.WARN, 'Some resolution scale does not compatibility this display. Please enter another resolution scale.')

    except (ValueError, TypeError, AttributeError) as error:
        messagebox.showerror('디아블로 런처', f'해상도 벡터 파싱중 예외가 발생하였습니다. 필수 파라미터가 누락되지 않았는지, 또는 잘못된 타입을 제공하지 않았는지 확인하시기 바랍니다. Exception code: {error}')
        logformat(errorLevel.ERR, f'Unknown data or parameter style: {envData}\n\t{error}')
        switchButton['state'] = "disabled"
        envData = None
        originX = None
        originY = None
        originFR = None
        alteredX = None
        alteredY = None
        alteredFR = None
    finally:
        logformat(errorLevel.INFO, f'{envData}')
        if resolutionProgram:
            logformat(errorLevel.INFO, f'Default resolution: {originX} X {originY} {originFR}Hz')
            logformat(errorLevel.INFO, f'Convert resolution: {alteredX} X {alteredY} {alteredFR}Hz')

def SetResolutionValue():
    messagebox.showinfo('해상도 벡터 편집기', '이 편집기는 본 프로그램에서만 적용되며 디아블로 런처를 종료 시 모든 변경사항이 유실됩니다. 변경사항을 영구적으로 적용하시려면 "고급 시스템 설정"을 이용해 주세요. ')
    envWindow = Tk()
    envWindow.title('해상도 벡터 편집기')
    envWindow.geometry("265x70+200+200")
    envWindow.resizable(False, False)
    envWindow.attributes('-toolwindow', True)

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

    originXtext.grid(row=0, column=0)
    envOriginX.grid(row=0, column=1)
    originYtext.grid(row=0, column=2)
    envOriginY.grid(row=0, column=3)
    originFRtext.grid(row=0, column=4)
    envOriginFR.grid(row=0, column=5)

    alteredXtext.grid(row=1, column=0)
    envAlteredX.grid(row=1, column=1)
    alteredYtext.grid(row=1, column=2)
    envAlteredY.grid(row=1, column=3)
    alteredFRtext.grid(row=1, column=4)
    envAlteredFR.grid(row=1, column=5)

    if envData is not None:
        envOriginX.insert(0, originX)
        envOriginY.insert(0, originY)
        envOriginFR.insert(0, originFR)
        envAlteredX.insert(0, alteredX)
        envAlteredY.insert(0, alteredY)
        envAlteredFR.insert(0, alteredFR)

    def commit():
        if envOriginX.get() == '' or envOriginY.get() == '' or envOriginFR.get() == '' or envAlteredX.get() == '' or envAlteredY.get() == '' or envAlteredFR.get() == '':
            messagebox.showwarning('해상도 벡터 편집기', '일부 환경변수가 누락되었습니다.')
            logformat(errorLevel.WARN, 'some env can not be None.')
            envWindow.after(1, envWindow.focus_force())
            return

        if (os.system(f'QRes /L | findstr /r "{envOriginX.get()}x" |findstr /r "{envOriginY.get()}," | findstr /r "\\<{envOriginFR.get()}\\>" > NUL 2>&1') != 0) or (os.system(f'QRes /L | findstr /r "{envAlteredX.get()}x" |findstr /r "{envAlteredY.get()}," | findstr /r "\\<{envAlteredFR.get()}\\>" > NUL 2>&1') != 0):
            messagebox.showwarning('해상도 벡터 편집기', '일부 해상도가 이 디스플레이와 호환되지 않습니다. 현재 디스플레이와 호환되는 다른 해상도를 입력해 주세요.')
            logformat(errorLevel.WARN, 'Some resolution scale does not compatibility this display. Please enter another resolution scale.')
            envWindow.after(1, envWindow.focus_force())
            return

        try:
            os.environ['DiabloLauncher'] = f'{envOriginX.get().replace(";", "")};{envOriginY.get().replace(";", "")};{envOriginFR.get().replace(";", "")};{envAlteredX.get().replace(";", "")};{envAlteredY.get().replace(";", "")};{envAlteredFR.get().replace(";", "")};'
            logformat(errorLevel.INFO, f"resolutionVector = {os.environ.get('DiabloLauncher')}")
            UpdateStatusValue()
            ReloadStatusBar()
            envWindow.destroy()
        except AttributeError as error:
            logformat(errorLevel.ERR, f"could not save env value: {error}")
            UpdateStatusValue()

    def openEnvSetting():
        msg_box = messagebox.askyesnocancel('디아블로 런처', '시스템 또는 계정의 환경변수 편집 시 업데이트된 환경변수를 반영하기 위해 프로그램을 종료해야 합니다. 시스템 환경변수를 수정할 경우 관리자 권한이 필요합니다. 대신 사용자 환경변수를 편집하시겠습니까?', icon='question')
        if msg_box is not None and msg_box:
            logformat(errorLevel.INFO, 'starting advanced user env editor... This action will not required UAC')
            subprocess.Popen('rundll32.exe sysdm.cpl,EditEnvironmentVariables')
            messagebox.showwarning('디아블로 런처', '사용자 환경변수 수정을 모두 완료한 후 다시 실행해 주세요.')
            logformat(errorLevel.INFO, 'advanced user env editor launched. DiabloLauncher now exiting...')
            ExitProgram()
        elif msg_box is not None and not msg_box:
            logformat(errorLevel.INFO, 'starting advanced system env editor... This action will required UAC')
            os.system('sysdm.cpl ,3')
            messagebox.showwarning('디아블로 런처', '시스템 환경변수 수정을 모두 완료한 후 다시 실행해 주세요.')
            logformat(errorLevel.INFO, 'advanced system env editor launched. DiabloLauncher now exiting...')
            ExitProgram()
        else:
            envWindow.after(1, envWindow.focus_force())

    envSet = Button(envWindow, text='고급 시스템 설정', command=openEnvSetting)
    commitBtn = Button(envWindow, text='적용', command=commit)

    if resolutionProgram:
        envSet.grid(row=3, column=1, columnspan=2)
        commitBtn.grid(row=3, column=4)
    else:
        envSet.pack(side=LEFT, padx=10)
        commitBtn.pack(side=RIGHT, padx=10)

    envWindow.mainloop()

def RequirementCheck():
    if not resolutionProgram:
        logformat(errorLevel.WARN, f'QRes not installed or not in...\n\t- C:\\Windows\\System32\n\t- {userLocalApp}/Program/Common/QRes.exe')
        if os.environ.get('IGN_RES_ALERT') != 'true':
            msg_box = messagebox.askquestion('디아블로 런처', '해상도를 변경하려면 QRes를 먼저 설치하여야 합니다. 지금 QRes를 다운로드 하시겠습니까?', icon='question')
            if msg_box == 'yes':
                webbrowser.open('https://www.softpedia.com/get/Multimedia/Video/Other-VIDEO-Tools/QRes.shtml')
        else:
            logformat(errorLevel.WARN, 'QRes install check dialog rejected due to "IGN_RES_ALERT" env prameter is true.\n\tPlease install QRes if would you like change display resolution.')
            print(f"\t{color.YELLOW.value}URL:{color.BLUE.value} https://www.softpedia.com/get/Multimedia/Video/Other-VIDEO-Tools/QRes.shtml{color.RESET.value}")
    elif envData is None:
        logformat(errorLevel.WARN, 'parameter does not set.')
        messagebox.showwarning('디아블로 런처', '해상도 벡터가 설정되어 있지 않습니다. "[도구]->[해상도 벡터 편집기]" 메뉴를 클릭하여 임시로 모든 기능을 사용해 보십시오.')

    if diablo2Path is None and diablo3Path is None and diablo4Path is None:
        logformat(errorLevel.WARN, 'The game does not exist in registry.')
        messagebox.showwarning('디아블로 런처', '이 컴퓨터에 디아블로 게임을 찾을 수 없습니다. 자세한 사항은 GitHub에 방문해 주세요.')

def UpdateStatusValue():
    FindGameInstalled()
    GetResolutionValue()
    now = datetime.now()
    cnt_time = now.strftime("%H:%M:%S")

    if resolutionProgram:
        status['text'] = f"\n정보 - {cnt_time}에 업데이트\n해상도 변경 지원됨: 예\n해상도 벡터: {f'{originX}x{originY} - {alteredX}x{alteredY}' if envData is not None else '알 수 없음'}\n현재 해상도: {f'{alteredX}x{alteredY} {alteredFR}Hz' if diabloExecuted else f'{originX}x{originY} {originFR}Hz'}\n디아블로 실행: {'예' if diabloExecuted else '아니요'}\n"
    else:
        status['text'] = f"\n정보 - {cnt_time}에 업데이트\n해상도 변경 지원됨: 아니요\n\n\n디아블로 실행: {'예' if diabloExecuted else '아니요'}\n"

def ReloadStatusBar():
    loadStart = time.time()
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

    if count > 10:
        statusbar['text'] = f"세션: {count}개 | 최고: {maxTime} | 평균: {avgTime} | 합계: {sumTime}"
        statusbar['anchor'] = CENTER
        toolsMenu.entryconfig(7, state='normal')
        Hovertip(statusbar, text=f"rev: {check_terminal_output('git rev-parse --short HEAD')} | RD: {check_terminal_output('git log -1 --date=format:%Y-%m-%d --format=%ad')} | 세션: {count}개 | 최고: {maxTime} | 평균: {avgTime} | 합계: {sumTime}", hover_delay=500)
    elif count > 2:
        statusbar['text'] = f"{check_terminal_output('git rev-parse --short HEAD')} | 세션: {count}개 | 최고: {maxTime} | 평균: {avgTime} | 합계: {sumTime}"
        statusbar['anchor'] = CENTER
        toolsMenu.entryconfig(7, state='normal')
        Hovertip(statusbar, text=f"rev: {check_terminal_output('git rev-parse --short HEAD')} | RD: {check_terminal_output('git log -1 --date=format:%Y-%m-%d --format=%ad')} | 세션: {count}개 | 최고: {maxTime} | 평균: {avgTime} | 합계: {sumTime}", hover_delay=500)
    elif count > 0:
        statusbar['text'] = f"{check_terminal_output('git rev-parse --short HEAD')} | 세션: {count}개 | 최고: {maxTime} | 평균: 데이터 부족 | 합계: {sumTime}"
        statusbar['anchor'] = CENTER
        toolsMenu.entryconfig(7, state='normal')
        Hovertip(statusbar, text=f"rev: {check_terminal_output('git rev-parse --short HEAD')} | RD: {check_terminal_output('git log -1 --date=format:%Y-%m-%d --format=%ad')} | 세션: {count}개 | 최고: {maxTime} | 평균: {avgTime} | 합계: {sumTime}", hover_delay=500)
    else:
        statusbar['text'] = f"{check_terminal_output('git rev-parse --short HEAD')} | 세션 통계를 로드할 수 없음"
        statusbar['anchor'] = W
        toolsMenu.entryconfig(7, state='disabled')
        Hovertip(statusbar, text=f"rev: {check_terminal_output('git rev-parse --short HEAD')} | RD: {check_terminal_output('git log -1 --date=format:%Y-%m-%d --format=%ad')} | 세션 통계를 로드할 수 없음", hover_delay=500)

def init():
    global switchButton
    global emergencyButton
    global status
    global statusbar
    global fileMenu
    global toolsMenu
    global aboutMenu
    global modMenu

    root.title("디아블로 런처")
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

    def ResetGameStatus():
        count, stat_max, stat_sum, stat_avg = LoadGameRunningTime()
        if count > 0:
            msg_box = messagebox.askyesno(title='디아블로 런처', message=f'통계 재설정을 수행할 경우 {count}개의 세션이 영원히 유실되며 되돌릴 수 없습니다. 만약의 경우를 대비하여 {userApp}/DiabloLauncher/runtime.log 파일을 백업하시기 바랍니다. 통계 재설정을 계속 하시겠습니까? ')
            if msg_box:
                ClearGameRunningTime()

    def ForceReload(*args):
        UpdateStatusValue()
        ReloadStatusBar()

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
        os.system('control.exe appwiz.cpl')

    def OpenDevSite():
        webbrowser.open('https://github.com/HyeongminKim/DiabloLauncher')

    def OpenDevIssues():
        now = datetime.now()
        cnt_time = now.strftime("%H:%M:%S")
        msg_box = messagebox.askyesno(title='디아블로 런처', message='이슈를 제보할 경우 터미널에 출력된 전체 로그와 경고창, 프로그램 화면 등을 첨부하여 주세요. 만약 가능하다면 어떠한 이유로 문제가 발생하였으며, 문제가 재현 가능한지 등을 첨부하여 주시면 좀 더 빠른 대응이 가능합니다. 지금 이슈 제보 페이지를 방문하시겠습니까?')
        if msg_box:
            logformat(errorLevel.INFO, f"=== Generated Report at {cnt_time} ===")
            logformat(errorLevel.INFO, f"Current agent: {platform.system()} {platform.release()}, Python {platform.python_version()}, {check_terminal_output('git --version')}")
            logformat(errorLevel.INFO, f"env data: {'configured' if envData is not None else 'None'}")
            if resolutionProgram:
                logformat(errorLevel.INFO, f"QRes version: {check_terminal_output('QRes /S | findstr QRes')}")
            else:
                logformat(errorLevel.INFO, "QRes version: None")
            logformat(errorLevel.INFO, f"Resolution vector: {f'{originX}x{originY} - {alteredX}x{alteredY}' if envData is not None and resolutionProgram else 'Unknown'}")

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
        about.geometry("480x310+400+400")
        about.deiconify()
        about.resizable(False, False)
        about.attributes('-toolwindow', True)

        def openBlizzardLegalSite():
            webbrowser.open('https://www.blizzard.com/en-us/legal/9c9cb70b-d1ed-4e17-998a-16c6df46be7b/copyright-notices')
        def openAppleLegalSite():
            webbrowser.open('https://www.apple.com/kr/legal/intellectual-property/guidelinesfor3rdparties.html')

        if resolutionProgram:
            logformat(errorLevel.INFO, "Resolution change program detected. Checking QRes version and license")
            text = Label(about, text=f"{platform.system()} {platform.release()}, Python {platform.python_version()}, {check_terminal_output('git --version')}\n\n--- Copyright ---\nDiablo II Resurrected, Diablo III, Diablo IV\n(c) 2022 BLIZZARD ENTERTAINMENT, INC. ALL RIGHTS RESERVED.\n\nDiablo Launcher\nCopyright (c) 2022-2023 Hyeongmin Kim\n\n{check_terminal_output('QRes /S | findstr QRes')}\n{check_terminal_output('QRes /S | findstr Copyright')}\n\n이 디아블로 런처에서 언급된 특정 상표는 각 소유권자들의 자산입니다.\n디아블로(Diablo), 블리자드(Blizzard)는 Blizzard Entertainment, Inc.의 등록 상표입니다.\nBootCamp, macOS는 Apple, Inc.의 등록 상표입니다.\n\n자세한 사항은 아래 버튼을 클릭해 주세요\n")
        else:
            logformat(errorLevel.INFO, "Resolution change program does not detected")
            text = Label(about, text=f"{platform.system()} {platform.release()}, Python {platform.python_version()}, {check_terminal_output('git --version')}\n\n--- Copyright ---\nDiablo II Resurrected, Diablo III, Diablo IV\n(c) 2022 BLIZZARD ENTERTAINMENT, INC. ALL RIGHTS RESERVED.\n\nDiablo Launcher\nCopyright (c) 2022-2023 Hyeongmin Kim\n\nQRes\nCopyright (C) Anders Kjersem.\n\n이 디아블로 런처에서 언급된 특정 상표는 각 소유권자들의 자산입니다.\n디아블로(Diablo), 블리자드(Blizzard)는 Blizzard Entertainment, Inc.의 등록 상표입니다.\nBootCamp, macOS는 Apple, Inc.의 등록 상표입니다.\n\n자세한 사항은 아래 버튼을 클릭해 주세요\n")
        blizzard = Button(about, text='블리자드 저작권 고지', command=openBlizzardLegalSite)
        apple = Button(about, text='애플컴퓨터 저작권 고지', command=openAppleLegalSite)

        text.grid(row=0, column=0, columnspan=2)
        blizzard.grid(row=1, column=0)
        apple.grid(row=1, column=1)
        about.mainloop()

    def BootCampSoundRecover():
        msg_box = messagebox.askyesno(title='디아블로 런처', message='"사운드 장치 문제해결" 메뉴는 사운드 장치가 Cirrus Logic일 경우에만 적용됩니다. 계속하시겠습니까?')
        if msg_box:
            soundRecover = Tk()
            soundRecover.title("Cirrus Logic 문제 해결")
            soundRecover.geometry("480x170+300+300")
            soundRecover.deiconify()
            soundRecover.resizable(False, False)
            soundRecover.attributes('-toolwindow', True)
            notice = Label(soundRecover, text='이 도움말의 일부 과정은 macOS의 BootCamp 지원 앱에서 수행해야 합니다.')
            contents = Label(soundRecover, text='1. BootCamp 지원 앱에서 Windows 지원 소프트웨어를 USB에 저장합니다.\n2. BootCamp로 재시동합니다.\n3. msconfig를 실행에 입력하여 부팅 옵션을 안전 부팅의 최소 설치로 선택합니다.\n4. BootCamp를 안전모드로 재시동합니다. \n5. 실행에 devmgmt.msc를 입력하여 장치관리자를 띄웁니다. \n6. Cirrus Logic 디바이스와 드라이버를 제거합니다.\n7. 1번에서 다운받은 폴더 경로를 드라이버 설치경로로 선택합니다. \n8. msconfig를 실행에 입력하여 안전부팅 체크박스를 해제합니다. \n9. BootCamp를 재시동합니다. ', anchor=W, justify=LEFT)
            notice.pack()
            contents.pack()
            soundRecover.mainloop()

    def OpenBattleNet():
        OpenProgramUsingRegistry(r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Battle.net')

    def OpenD2RModDir():
        if diablo2Path is not None:
            logformat(errorLevel.INFO, f'The {diablo2Path}/mods directory exist. The target directory will now open.')
            os.startfile(f'"{diablo2Path}/mods"')

    def ModApplyHelp():
        if definedMod is not None and definedMod != "":
            try:
                import clipboard
            except (ModuleNotFoundError, ImportError) as error:
                logformat(errorLevel.WARN, f'Unable to copy mods name: " -mod {definedMod} -txt". reason: {error}. retrying copy string with alternative module...')
                try:
                    import pyperclip
                except (ModuleNotFoundError, ImportError) as error:
                    logformat(errorLevel.ERR, f'Unable to copy mods name: " -mod {definedMod} -txt". reason: {error}. all known module was not installed yet. please copy it manually.')
                    messagebox.showinfo(title='디아블로 모드', message=f'Diablo II Resurrected에 모드를 적용하기 위해서 명령행 인수에 " -mod {definedMod} -txt"를 입력해야 합니다.')
                    launch.after(1, launch.focus_force())
                else:
                    msg_box = messagebox.askyesno(title='디아블로 모드', message=f'Diablo II Resurrected에 모드를 적용하기 위해서 명령행 인수에 " -mod {definedMod} -txt"를 입력해야 합니다. 편리하게 명령행 인수를 입력하기 위해 제공된 파라미터를 클립보드에 복사하시겠습니까?')
                    if msg_box:
                        pyperclip.copy(f' -mod {definedMod} -txt')
                        logformat(errorLevel.INFO, f'Successfully copied mods name: " -mod {definedMod} -txt" with pyperclip module.')
                        del pyperclip
                        logformat(errorLevel.INFO, 'unloaded pyperclip module.')
                    else:
                        logformat(errorLevel.INFO, 'user aborted copy mods name: pyperclip module detected, however it was not imported. ')
                    launch.after(1, launch.focus_force())
            else:
                msg_box = messagebox.askyesno(title='디아블로 모드', message=f'Diablo II Resurrected에 모드를 적용하기 위해서 명령행 인수에 " -mod {definedMod} -txt"를 입력해야 합니다. 편리하게 명령행 인수를 입력하기 위해 제공된 파라미터를 클립보드에 복사하시겠습니까?')
                if msg_box:
                    clipboard.copy(f' -mod {definedMod} -txt')
                    logformat(errorLevel.INFO, f'Successfully copied mods name: " -mod {definedMod} -txt" with clipboard module.')
                    del clipboard
                    logformat(errorLevel.INFO, 'unloaded clipboard module.')
                else:
                    logformat(errorLevel.INFO, 'user aborted copy mods name: clipboard module detected, however it was not imported. ')
                launch.after(1, launch.focus_force())
        else:
            logformat(errorLevel.INFO, 'Unable to load mods detail. no such file or directory.')
            messagebox.showinfo(title='디아블로 모드', message='Diablo II Resurrected에 모드를 적용하기 위해서 명령행 인수에 " -mod modName -txt"를 입력해야 합니다.')
            launch.after(1, launch.focus_force())

    def ModGeneralHelp():
        messagebox.showinfo(title='디아블로 모드', message='"없는 문자열" 오류가 발생할 경우 모드팩 업데이트가 출시 되었는지 확인하시거나, json파일의 모든 누락된 ID를 직접 추가해 주세요. 자세한 사항은 "모드 업데이트 방법"을 참조해 주세요')
        launch.after(1, launch.focus_force())

    def ModAdvancedHelp():
        msg_box = messagebox.askyesno(title='디아블로 모드', message='Diablo II Resurrected 모드 생성 또는 편집시 유용한 프로그램 리스트를 확인하시겠습니까?')
        if msg_box:
            webbrowser.open('https://github.com/eezstreet/D2RModding-SpriteEdit')
            webbrowser.open('http://www.zezula.net/en/casc/main.html')
            webbrowser.open('https://github.com/Cjreek/D2ExcelPlus')
            webbrowser.open('https://github.com/WinMerge/winimerge')
            webbrowser.open('https://github.com/microsoft/vscode')
        launch.after(1, launch.focus_force())

    def ModHelpWindow():
        launch.title('모드 도움말')

        note = Label(launch, text='사용가능한 도움말', height=2)
        applyHelp = Button(launch, text='모드 적용방법', width=20, height=5, command=ModApplyHelp)

        if definedMod is not None and definedMod != "":
            logformat(errorLevel.INFO, 'mods resolve problem button was enabled.')
            generalHelp = Button(launch, text=f'{definedMod} 모드\n문제해결', width=20, height=2, command=ModGeneralHelp, state='normal')
            advancedHelp = Button(launch, text='모드 업데이트 방법', width=20, height=2, command=ModAdvancedHelp, state='normal')
        else:
            logformat(errorLevel.INFO, 'mods resolve problem button was disabled. reason: Unable to load mods detail. no such file or directory.')
            generalHelp = Button(launch, text='모드 문제해결', width=20, height=3, command=ModGeneralHelp, state='disabled')
            advancedHelp = Button(launch, text='새로운 모드 생성', width=20, height=2, command=ModAdvancedHelp, state='normal')

        note.grid(row=0, column=0, columnspan=2)
        generalHelp.grid(row=1, column=0)
        advancedHelp.grid(row=2, column=0)
        applyHelp.grid(row=1, column=1, rowspan=3)
        ShowWindow()
        launch.mainloop()

    menubar = Menu(root)
    fileMenu = Menu(menubar, tearoff=0)
    fileMenu.add_command(label='D2R 디렉토리 열기', command=OpenD2RDir, state='disabled')
    fileMenu.add_command(label='Diablo III 디렉토리 열기', command=OpenD3Dir, state='disabled')
    fileMenu.add_command(label='Diablo IV 디렉토리 열기', command=OpenD4Dir, state='disabled')
    fileMenu.add_command(label='통계 디렉토리 열기', command=OpenGameStatusDir, state='disabled')
    fileMenu.add_separator()

    if TestRegistryValue(r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Battle.net'):
        fileMenu.add_command(label='Battle.net 실행', command=OpenBattleNet, state='normal')
    else:
        fileMenu.add_command(label='Battle.net 실행', command=OpenBattleNet, state='disabled')

    menubar.add_cascade(label='파일', menu=fileMenu)

    toolsMenu = Menu(menubar, tearoff=0)
    toolsMenu.add_command(label='새로 고침', command=ForceReload, accelerator='F5')
    toolsMenu.add_command(label='런처 업데이트 확인...', command=UpdateProgram)
    toolsMenu.add_separator()
    if resolutionProgram:
        toolsMenu.add_command(label='해상도 벡터 편집기...', command=SetResolutionValue, state='normal')
    else:
        toolsMenu.add_command(label='해상도 벡터 편집기...', command=SetResolutionValue, state='disabled')

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
    aboutMenu.add_command(label='GitHub 방문', command=OpenDevSite)
    aboutMenu.add_command(label='이 디아블로 런처에 관하여...', command=AboutThisApp, accelerator='F1')
    aboutMenu.add_separator()

    logLevel = os.environ.get('LOG_VERBOSE_LEVEL')
    if logLevel is not None and logLevel == "verbose":
        aboutMenu.add_command(label='버그 신고...', command=OpenDevIssues, state='normal')
    else:
        aboutMenu.add_command(label='버그 신고...', command=OpenDevIssues, state='disabled')

    menubar.add_cascade(label='정보', menu=aboutMenu)

    root.bind_all("<F5>", ForceReload)
    root.bind_all("<F1>", AboutThisApp)

    welcome = Label(root, text='')
    switchButton = Button(rootFrame, text='디아블로 실행...', command=LaunchGameAgent, width=35, height=5, state='disabled')
    emergencyButton = Button(rootFrame, text='긴급 전원 작업\n(게임 저장 후 실행 요망)', width=35, height=5, command=EmgergencyReboot)

    switchButton.grid(column=0, row=0)
    emergencyButton.grid(column=1, row=0)

    now = datetime.now()
    cnt_time = now.strftime("%H:%M:%S")

    CheckResProgram()
    FindGameInstalled()
    GetResolutionValue()
    RequirementCheck()

    if resolutionProgram:
        status = Label(root, text=f"\n정보 - {cnt_time}에 업데이트\n해상도 변경 지원됨: 예\n해상도 벡터: {f'{originX}x{originY} - {alteredX}x{alteredY}' if envData is not None else '알 수 없음'}\n현재 해상도: {f'{alteredX}x{alteredY} {alteredFR}Hz' if diabloExecuted else f'{originX}x{originY} {originFR}Hz'}\n디아블로 실행: {'예' if diabloExecuted else '아니요'}\n")
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

    root.config(menu=menubar)

    root.mainloop()

if __name__ == '__main__':
    logLevel = os.environ.get('LOG_VERBOSE_LEVEL')
    if logLevel is not None and logLevel == "verbose":
        multiprocessing.log_to_stderr()
        logger = multiprocessing.get_logger()
        logger.setLevel(logging.INFO)

    mainThread = multiprocessing.Process(target=init)
    updateThread = multiprocessing.Process(target=UpdateProgram)

    mainThread.start()
    updateThread.start()

    mainThread.join()
    updateThread.join()
