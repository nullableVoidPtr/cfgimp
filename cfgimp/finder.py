from importlib.abc import PathEntryFinder
from cfgimp.loaders import _DEFAULT_CFGIMP_LOADERS, BaseLoader, StubLoader
from pathlib import Path
import importlib.util
from typing import Dict


class CfgImpPathFinder(PathEntryFinder):
    path_entry: Path
    target_package: str
    loaders: Dict[str, BaseLoader]


    def __init__(self, path_entry, target_package, loaders=_DEFAULT_CFGIMP_LOADERS):
        self.path_entry = Path(path_entry).resolve()
        self.target_package = target_package
        self.loaders = {
            loader.extension: loader
            for loader in loaders
            if loader.extension is not None
        }

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
