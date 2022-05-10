from .base import BaseModule
from importlib.machinery import ModuleSpec


class UnresolvedModule(BaseModule):
    def __init__(self, spec: ModuleSpec):
        super().__init__(spec)

    def __repr__(self):
        return (
            f"<unresolved module '{self.__name__}' (either '"
            + "' or '".join(self.__path__)
            + "')>"
        )
