# pylint: disable=W0613

from enum import Enum

class parentLocation(Enum):
    UserAppData: (str | None)
    UserLocalAppData: (str | None)
    ProgramData: (str | None)

def loadSettings(scope: parentLocation, target_key: list[str]) -> (any | None): ...
def dumpSettings(scope: parentLocation, target_key: list[str], target_value: any) -> bool: ...

def makeConfigurationFileStructures(scope: parentLocation) -> None: ...
def checkConfigurationStructure(scope: parentLocation, target_key: list[str]) -> None: ...
