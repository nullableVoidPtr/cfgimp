from .base import BaseModule
from collections.abc import MutableSequence
from importlib.machinery import ModuleSpec
from typing import List, Any


class ArrayModule(BaseModule, MutableSequence):
    array: List[Any]

    def __init__(self, spec: ModuleSpec):
        super().__init__(spec)
        self.array = []

    def __getitem__(self, key):
        return self.array[key]

    def __setitem__(self, key, value):
        self.array[key] = value

    def __delitem__(self, key):
        del self.array[key]

    def __len__(self):
        return len(self.array)

    def insert(self, index, value):
        self.array.insert(index, value)

    def __str__(self):
        return str(self.array)

    def __repr__(self):
        return f"<array module '{self.__name__}' from '{self.__file__}'>"
