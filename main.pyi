# pylint: disable=W0613

userApp: str | None
userLocalApp: str | None

diabloExecuted: bool
updateChecked: bool
forceReboot: bool

rebootWaitTime: bytes
loadWaitTime: bytes

gameStartTime: None | float
gameEndTime: None | float

envData: None | str
diablo2Path: None | str
diablo3Path: None | str
diablo4Path: None | str

definedMod: None | str
resolutionProgram: bool

originX: None | str
originY: None | str
originFR: None | str
alteredX: None | str
alteredY: None | str
alteredFR: None | str

def ShowWindow() -> None: ...
def HideWindow() -> None: ...
def AlertWindow() -> None: ...

def CheckResProgram() -> None: ...
def CheckDarkMode() -> bool: ...
def UpdateProgram() -> None: ...

def ExitProgram() -> None: ...
def InterruptProgram(sig, frame) -> None: ...

def LoadGameRunningTime(playTime: float) -> (tuple[int, float | int, float, float] | tuple[int, float | int, int, int] | tuple[int, int, int, int]): ...

def GameLauncher(gameName: str, supportedX: int, supportedY: int, os_min: int) -> None: ...
def LaunchGameAgent() -> None: ...

def BootAgent(poweroff: str) -> None: ...
def EmgergencyReboot() -> None: ...

def GetModDetails() -> None: ...
def DownloadModsLink() -> None: ...
def SearchModInGitHub() -> None: ...
def ModsPreferSelector() -> None: ...

def FindGameInstalled() -> None: ...
def GetResolutionValue() -> None: ...
def SetResolutionValue() -> None: ...

def RequirementCheck() -> None: ...

def UpdateStatusValue() -> None: ...
def ReloadStatusBar() -> None: ...

def init() -> None: ...
