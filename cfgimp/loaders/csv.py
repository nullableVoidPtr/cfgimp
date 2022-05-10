from .base import BaseLoader
from importlib.machinery import ModuleSpec
from cfgimp.modules import ArrayModule
import csv


class CsvLoader(BaseLoader):
    extension = "csv"

    def create_module(self, spec: ModuleSpec):
        return ArrayModule(spec)

    def exec_module(self, module):
        with open(module.__file__, "r") as f:
            module.clear()
            module.extend(csv.reader(f))
        module.install_suffix()
