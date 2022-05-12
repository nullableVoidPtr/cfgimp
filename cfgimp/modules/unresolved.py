from .base import BaseModule


class UnresolvedModule(BaseModule):
    def install_suffix(self):
        pass

    def __repr__(self):
        return (
            f"<unresolved module '{self.__name__}' (either '"
            + "' or '".join(self.__path__)
            + "')>"
        )
