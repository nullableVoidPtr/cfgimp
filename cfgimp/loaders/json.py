import json
from importlib.machinery import ModuleSpec

from cfgimp.modules import TableModule

from .base import BaseLoader


class JsonLoader(BaseLoader):
    extension = "json"

    def create_module(self, spec: ModuleSpec):
        return TableModule(spec)

    def exec_module(self, module):
        with open(module.__file__, "r") as f:
            module.update(json.load(f))
        module.install_suffix()
