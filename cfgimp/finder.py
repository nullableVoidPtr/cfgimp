import importlib.util
from importlib.abc import PathEntryFinder
from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Optional, Type

from cfgimp.loaders import _DEFAULT_CFGIMP_LOADERS, BaseLoader, StubLoader


class CfgImpPathFinder(PathEntryFinder):
    path_entry: Path
    target_package: str
    loaders: Dict[str, Type[BaseLoader]]

    def __init__(
        self,
        path_entry: Path | str,
        target_package: str,
        loaders: Optional[List[Type[BaseLoader]]] = None,
    ):
        self.path_entry = Path(path_entry).resolve()
        self.target_package = target_package

        if loaders is None:
            loaders = _DEFAULT_CFGIMP_LOADERS

        self.loaders = {
            loader.extension: loader
            for loader in loaders
            if loader.extension is not None
        }

    def find_spec(
        self,
        fullname: str,
        target: Optional[ModuleType] = None,  # pylint: disable=unused-argument
    ) -> Optional[ModuleSpec]:
        parent = fullname
        name = None
        if "." in parent:
            parent, name = parent.rsplit(".", 1)
        if not parent.startswith(self.target_package):
            return None

        resolved_specs: List[ModuleSpec] = []
        for file_path in (
            self.path_entry.iterdir() if self.path_entry.is_dir() else [self.path_entry]
        ):
            if not file_path.is_file():
                continue

            stem, suffix = file_path.name.split(".", 1)
            if suffix not in self.loaders:
                continue

            if "." in parent and stem == parent.rsplit(".", 1)[1] and name == suffix:
                # import package.filename.extension
                if spec := importlib.util.spec_from_file_location(
                    fullname,
                    file_path,
                    loader=self.loaders[suffix](fullname, file_path),
                ):
                    resolved_specs.append(spec)
            elif stem == name:
                # import package.filename
                if spec := importlib.util.spec_from_file_location(
                    fullname,
                    file_path,
                    loader=self.loaders[suffix](fullname, file_path),
                    submodule_search_locations=[str(file_path)],
                ):
                    resolved_specs.append(spec)

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
                        getattr(spec, "submodule_search_locations", [])
                        for spec in resolved_specs
                    ]
                    for f in locations
                ],
            )

        return resolved_specs[0]
