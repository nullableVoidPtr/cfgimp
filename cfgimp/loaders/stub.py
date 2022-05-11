from importlib.abc import Loader
from importlib.machinery import ModuleSpec

from cfgimp.modules import UnresolvedModule


class StubLoader(Loader):
    def __init__(self, fullname):
        self.fullname = fullname

    def create_module(self, spec: ModuleSpec):
        return UnresolvedModule(spec)

    def exec_module(self, module):
        pass
