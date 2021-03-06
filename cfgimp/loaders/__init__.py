from .base import BaseLoader
from .csv import CsvLoader
from .json import JsonLoader
from .stub import StubLoader

__all__ = ["BaseLoader", "JsonLoader", "CsvLoader", "StubLoader"]

try:
    from .toml import TomlLoader  # noqa
except ImportError:
    pass
else:
    __all__.append("TomlLoader")

_DEFAULT_CFGIMP_LOADERS = BaseLoader.__subclasses__()

__all__.append("_DEFAULT_CFGIMP_LOADERS")
