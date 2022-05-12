from importlib.abc import Loader
from pathlib import Path
from typing import ClassVar, Optional


class BaseLoader(Loader):
    extension: ClassVar[Optional[str]] = None
    fullname: str
    path: str | Path

    def __init__(self, fullname: str, path: str | Path):
        self.fullname = fullname
        self.path = path
