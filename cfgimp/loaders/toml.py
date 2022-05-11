from importlib.machinery import ModuleSpec

import toml

from cfgimp.modules import TableModule

from .base import BaseLoader


class TomlLoader(BaseLoader):
    extension = "toml"

    def create_module(self, spec: ModuleSpec):
        return TableModule(spec)

    def exec_module(self, module):
        with open(module.__file__, "r") as f:
            module.update(toml.load(f))
        module.install_suffix()
