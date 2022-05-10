from typing import Sequence, List, Type
from importlib.abc import PathEntryFinder
from cfgimp.loaders import BaseLoader, _DEFAULT_CFGIMP_LOADERS
from cfgimp.finder import CfgImpPathFinder
import sys


class CfgImp:
    target_package: str
    loaders: List[Type[BaseLoader]]

    def __init__(self, target_package: str, loaders: Sequence[Type[BaseLoader] | str] = _DEFAULT_CFGIMP_LOADERS): 
        self.target_package = target_package
        self.loaders = []
        for loader in loaders:
            if not isinstance(loader, str) and issubclass(loader, BaseLoader):
                self.loaders.append(loader)
                continue

            matches = list(filter(lambda l: loader == getattr(l, "extension", None), _DEFAULT_CFGIMP_LOADERS))
            if len(matches) == 0:
                raise ValueError("An extension was specified but no loader was found.")

            self.loaders.append(matches[0])

    def __call__(self, path_entry: str) -> PathEntryFinder:
        return CfgImpPathFinder(path_entry, self.target_package)

    def install(self):
        sys.path_hooks.insert(0, self)

    def uninstall(self):
        sys.path_hooks.remove(self)
