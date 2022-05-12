import sys
from importlib.abc import PathEntryFinder
from typing import List, Optional, Sequence, Type

from cfgimp.finder import CfgImpPathFinder
from cfgimp.loaders import _DEFAULT_CFGIMP_LOADERS, BaseLoader


class CfgImp:
    target_package: str
    loaders: List[Type[BaseLoader]]

    def __init__(
        self,
        target_package: str,
        loaders: Optional[Sequence[Type[BaseLoader] | str]] = None,
    ):
        self.target_package = target_package

        if loaders is None:
            loaders = _DEFAULT_CFGIMP_LOADERS

        self.loaders = []
        for loader in loaders:
            if not isinstance(loader, str) and issubclass(loader, BaseLoader):
                self.loaders.append(loader)
                continue

            matches = list(
                filter(
                    lambda l: getattr(l, "extension", None)
                    == loader,  # pylint: disable=cell-var-from-loop
                    _DEFAULT_CFGIMP_LOADERS,
                )
            )
            if len(matches) == 0:
                raise ValueError("An extension was specified but no loader was found.")

            self.loaders.append(matches[0])

    def __call__(self, path_entry: str) -> PathEntryFinder:
        return CfgImpPathFinder(path_entry, self.target_package, self.loaders)

    def install(self):
        sys.path_hooks.insert(0, self)

    def uninstall(self):
        sys.path_hooks.remove(self)
