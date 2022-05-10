from types import ModuleType
from importlib.machinery import ModuleSpec
import sys


class BaseModule(ModuleType):
    def __init__(self, spec: ModuleSpec):
        super().__init__(spec.name)
        self.__loader__ = spec.loader
        self.__package__ = spec.parent
        self.__spec__ = spec
        self.__file__ = spec.origin
        self.__path__ = getattr(spec, "submodule_search_locations", [])

    def install_suffix(self):
        if self.__loader__.extension is not None:
            ext = self.__loader__.extension
            if not self.__name__.endswith("." + ext):
                self.__name__ += "." + ext
                sys.modules[self.__name__] = self
                setattr(self, ext, self)
