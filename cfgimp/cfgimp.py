import importlib.abc
import importlib.util
import importlib.machinery
from pathlib import Path
from types import ModuleType
import collections.abc
import sys
import json
import csv


class BaseModule(ModuleType):
    def __init__(self, spec: importlib.machinery.ModuleSpec):
        super().__init__(spec.name)
        self.__loader__ = spec.loader
        self.__package__ = spec.parent
        self.__spec__ = spec
        self.__file__ = spec.origin
        self.__path__ = spec.submodule_search_locations

    def install_suffix(self):
        if hasattr(self.__loader__, "extension"):
            ext = self.__loader__.extension
            if not self.__name__.endswith("." + ext):
                self.__name__ += "." + ext
                sys.modules[self.__name__] = self
                setattr(self, ext, self)


class TableModule(BaseModule, collections.abc.MutableMapping):
    def __init__(self, spec: importlib.machinery.ModuleSpec):
        super().__init__(spec)
        self.table = {}

    def __getitem__(self, key):
        return self.table[key]

    def __setitem__(self, key, value):
        self.table[key] = value

    def __delitem__(self, key):
        del self.table[key]

    def __iter__(self):
        return self.table.__iter__()

    def __len__(self):
        return len(self.table)

    def __str__(self):
        return str(self.table)

    def __repr__(self):
        return f"<table module '{self.__name__}' from '{self.__file__}'>"


class ArrayModule(BaseModule, collections.abc.MutableSequence):
    def __init__(self, spec: importlib.machinery.ModuleSpec):
        super().__init__(spec)
        self.array = []

    def __getitem__(self, key):
        return self.array[key]

    def __setitem__(self, key, value):
        self.array[key] = value

    def __delitem__(self, key):
        del self.array[key]

    def __len__(self):
        return len(self.array)

    def insert(self, index, value):
        self.array.insert(index, value)

    def __str__(self):
        return str(self.array)

    def __repr__(self):
        return f"<array module '{self.__name__}' from '{self.__file__}'>"


class CfgImpLoader(importlib.abc.Loader):
    def __init__(self, fullname, path):
        self.fullname = fullname
        self.path = path

    def is_package(self, fullname):
        if fullname != self.fullname:
            return False

        if hasattr(self, "extension") and fullname.endswith("." + self.extension):
            return False

        return True


class JsonLoader(CfgImpLoader):
    extension = "json"

    def create_module(self, spec: importlib.machinery.ModuleSpec):
        return TableModule(spec)

    def exec_module(self, module):
        with open(module.__file__, "r") as f:
            module.update(json.load(f))
        module.install_suffix()


class CsvLoader(CfgImpLoader):
    extension = "csv"

    def create_module(self, spec: importlib.machinery.ModuleSpec):
        return ArrayModule(spec)

    def exec_module(self, module):
        with open(module.__file__, "r") as f:
            module.clear()
            module.extend(csv.reader(f))
        module.install_suffix()


_DEFAULT_CFGIMP_LOADERS = {
    loader.extension: loader for loader in CfgImpLoader.__subclasses__()
}


class UnresolvedModule(BaseModule):
    def __init__(self, spec: importlib.machinery.ModuleSpec):
        super().__init__(spec)

    def __repr__(self):
        return (
            f"<unresolved module '{self.__name__}' (either '"
            + "' or '".join(self.__path__)
            + "')>"
        )


class StubLoader(importlib.abc.Loader):
    def __init__(self, fullname):
        self.fullname = fullname

    def create_module(self, spec: importlib.machinery.ModuleSpec):
        return UnresolvedModule(spec)

    def exec_module(self, module):
        pass


class CfgImpPathFinder(importlib.abc.PathEntryFinder):
    def __init__(self, path_entry, target_package, loaders=_DEFAULT_CFGIMP_LOADERS):
        self.path_entry = Path(path_entry).resolve()
        self.loaders = loaders
        self.target_package = target_package

    def find_spec(self, fullname, target=None):
        parent = fullname
        name = None
        if "." in parent:
            parent, name = parent.rsplit(".", 1)
        if not parent.startswith(self.target_package):
            return None

        resolved_specs = []
        for f in (
            self.path_entry.iterdir() if self.path_entry.is_dir() else [self.path_entry]
        ):
            if f.is_file():
                stem, suffix = f.name.split(".", 1)
                if suffix not in self.loaders:
                    continue

                if (
                    "." in parent
                    and stem == parent.rsplit(".", 1)[1]
                    and name == suffix
                ):
                    # import package.filename.extension
                    resolved_specs.append(
                        importlib.util.spec_from_file_location(
                            fullname,
                            f,
                            loader=self.loaders[suffix](fullname, f),
                        )
                    )
                elif stem == name:
                    # import package.filename
                    resolved_specs.append(
                        importlib.util.spec_from_file_location(
                            fullname,
                            f,
                            loader=self.loaders[suffix](fullname, f),
                            submodule_search_locations=[str(f)],
                        )
                    )

        if len(resolved_specs) == 0:
            return None

        if len(resolved_specs) > 1:
            return importlib.util.spec_from_file_location(
                fullname,
                self.path_entry,
                loader=StubLoader(fullname),
                submodule_search_locations=[
                    f
                    for locations in [
                        spec.submodule_search_locations for spec in resolved_specs
                    ]
                    for f in locations
                ],
            )

        return resolved_specs[0]


class CfgImp:
    def __init__(self, target_package):
        self.target_package = target_package

    def __call__(self, path_entry):
        return CfgImpPathFinder(path_entry, self.target_package)

    @staticmethod
    def install(finder):
        sys.path_hooks.insert(0, finder)
