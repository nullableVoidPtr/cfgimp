from importlib.abc import Loader
from typing import Optional, ClassVar
from pathlib import Path


class BaseLoader(Loader):
    extension: ClassVar[Optional[str]] = None
    fullname: str
    path: str | Path

    def __init__(self, fullname: str, path: str | Path):
        self.fullname = fullname
        self.path = path

    def is_package(self, fullname: str):
        if fullname != self.fullname:
            return False

        if self.extension is not None and fullname.endswith("." + self.extension):
            return False

        return True
