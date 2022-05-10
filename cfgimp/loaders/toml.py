from .base import BaseLoader
from importlib.machinery import ModuleSpec
from cfgimp.modules import TableModule
import toml


class TomlLoader(BaseLoader):
    extension = "toml"

    def create_module(self, spec: ModuleSpec):
        return TableModule(spec)

    def exec_module(self, module):
        with open(module.__file__, "r") as f:
            module.update(toml.load(f))
        module.install_suffix()
