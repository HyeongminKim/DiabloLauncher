# pylint: disable=W0613

ignoreTime: bytes

def FormatTime(milliseconds: float, rawType: bool) -> (tuple[int, int, int] | str): ...
def SaveGameRunningTime(playTime: float) -> None: ...
def LoadGameRunningTime(playTime: float) -> (tuple[int, float | int, float, float] | tuple[int, float | int, int, int] | tuple[int, int, int, int]): ...
def ClearGameRunningTime() -> None: ...
