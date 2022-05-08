import importlib.abc
import importlib.util
import importlib.machinery
from pathlib import Path
import sys
import json
import csv
import warnings


class CfgImpTableModule(dict):
    def __init__(self, spec: importlib.machinery.ModuleSpec):
        super().__init__(self)
        self.__name__ = spec.name
        self.__package__ = spec.parent
        self.__file__ = spec.origin
        self.__loader__ = spec.loader

    def __str__(self):
        return super().__repr__()

    def __repr__(self):
        return f"<module '{self.__name__}' from '{self.__file__}'>"


class CfgImpArrayModule(list):
    def __init__(self, spec: importlib.machinery.ModuleSpec):
        super().__init__(self)
        self.__name__ = spec.name
        self.__package__ = spec.parent
        self.__file__ = spec.origin
        self.__loader__ = spec.loader

    def __str__(self):
        return super().__repr__()

    def __repr__(self):
        return f"<module '{self.__name__}' from '{self.__file__}'>"


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

    def __init__(self, fullname, path):
        super().__init__(fullname, path)

    def create_module(self, spec: importlib.machinery.ModuleSpec):
        return CfgImpTableModule(spec)

    def exec_module(self, module):
        with open(module.__file__, "r") as f:
            module.update(json.load(f))


class CsvLoader(CfgImpLoader):
    extension = "csv"

    def __init__(self, fullname, path):
        super().__init__(fullname, path)

    def create_module(self, spec: importlib.machinery.ModuleSpec):
        return CfgImpArrayModule(spec)

    def exec_module(self, module):
        with open(module.__file__, "r") as f:
            module.clear()
            module.extend(csv.reader(f))


_DEFAULT_CFGIMP_LOADERS = {
    loader.extension: loader for loader in CfgImpLoader.__subclasses__()
}


class UnresolvedModule:
    def __init__(self, spec: importlib.machinery.ModuleSpec, files):
        self.__name__ = spec.name
        self.__package__ = spec.parent
        self.__loader__ = spec.loader
        self.__path__ = [spec.origin]
        self.files = files

    def __repr__(self):
        return f"<unresolved module '{self.__name__}' (either {' or '.join(map(str, self.files))})>"


class StubLoader(importlib.abc.Loader):
    def __init__(self, fullname, files):
        self.fullname = fullname
        self.files = files

    def create_module(self, spec: importlib.machinery.ModuleSpec):
        return UnresolvedModule(spec, self.files)

    def exec_module(self, module):
        pass

    def is_package(self, fullname):
        if fullname == self.fullname:
            return True

        return False


class CfgImpPathFinder(importlib.abc.PathEntryFinder):
    def __init__(self, path_entry, target_package, loaders=_DEFAULT_CFGIMP_LOADERS):
        self.path_entry = Path(path_entry).resolve()
        self.loaders = loaders
        self.target_package = target_package

    def find_spec(self, fullname, target=None):
        parent = fullname
        if "." in parent:
            parent, name = parent.rsplit(".", 1)
        if not parent.startswith(self.target_package):
            return None

        found_loaders = []
        for f in self.path_entry.iterdir():
            if f.is_file():
                stem, suffix = f.name.split(".", 1)
                if (
                    "." in parent
                    and stem == parent.rsplit(".", 1)[1]
                    and name == suffix
                    and suffix in self.loaders
                ):
                    # import package.filename.extension
                    found_loaders.append((self.loaders[suffix], (fullname, f)))
                elif stem == name and suffix in self.loaders:
                    # import package.filename
                    found_loaders.append((self.loaders[suffix], (fullname, f)))

        if len(found_loaders) == 0:
            return None
        elif len(found_loaders) > 1:
            return importlib.util.spec_from_loader(
                fullname,
                StubLoader(fullname, [found[1][1] for found in found_loaders]),
                origin=str(self.path_entry),
                is_package=True,
            )

        loader_details = found_loaders[0]
        return importlib.util.spec_from_file_location(
            *loader_details[1],
            loader=loader_details[0](*loader_details[1]),
        )


class CfgImp:
    def __init__(self, target_package):
        self.target_package = target_package

    def __call__(self, path_entry):
        return CfgImpPathFinder(path_entry, self.target_package)

    @staticmethod
    def install(finder):
        sys.path_hooks.insert(0, finder)
        # sys.meta_path.insert(0, CfgImpMetaFinder(finder.target_package))
