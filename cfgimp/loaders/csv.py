import csv
from importlib.machinery import ModuleSpec

from cfgimp.modules import ArrayModule

from .base import BaseLoader


class CsvLoader(BaseLoader):
    extension = "csv"

    def create_module(self, spec: ModuleSpec):
        return ArrayModule(spec)

    def exec_module(self, module):
        with open(module.__file__, "r", encoding="utf-8") as file:
            module.clear()
            module.extend(csv.reader(file))
        module.install_suffix()
