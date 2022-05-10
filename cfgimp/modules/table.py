from .base import BaseModule
from collections.abc import MutableMapping
from importlib.machinery import ModuleSpec
from typing import Iterator, Dict, Any


class TableModule(BaseModule, MutableMapping):
    table: Dict[str, Any]

    def __init__(self, spec: ModuleSpec):
        super().__init__(spec)
        self.table = {}

    def __getitem__(self, key: str) -> Any:
        return self.table[key]

    def __setitem__(self, key: str, value: Any):
        self.table[key] = value

    def __delitem__(self, key: str):
        del self.table[key]

    def __iter__(self) -> Iterator[Any]:
        return self.table.__iter__()

    def __len__(self) -> int:
        return len(self.table)

    def __str__(self) -> str:
        return str(self.table)

    def __repr__(self) -> str:
        return f"<table module '{self.__name__}' from '{self.__file__}'>"
