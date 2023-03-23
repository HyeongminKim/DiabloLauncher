# pylint: disable=W0613

from enum import Enum

logLevel: str | None

class color(Enum):
    RESET: str
    RED: str
    GREEN: str
    YELLOW: str
    BLUE: str
    MAGENTA: str
    GRAY: str

class errorLevel(Enum):
    INFO: bytes
    WARN: bytes
    ERR: bytes
    FATL: bytes

def logformat(level: errorLevel, text: str) -> None: ...
