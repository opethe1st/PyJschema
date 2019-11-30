import dataclasses as d
import typing as t


# wanted to make this similar to List and Dict
# so instances of this class could be used as drop in
# replacements for the native types
# but it seems impossible to do
# TODO: Refactor - rename this file to builtins wrapper
@d.dataclass
class Primitive:
    value: t.Any
    location: str


class List(list):
    def __init__(self, value, location=None):
        self.location = location
        super().__init__(value)

    def __eq__(self, other):
        if isinstance(other, dict):
            return super().__eq__(other)
        if not isinstance(other, List):
            return False
        return super().__eq__(other) and self.location == other.location

    def __str__(self):
        return f"{self.__class__.__name__}({self!r}, location={self.location})"


class Dict(dict):
    def __init__(self, value, location=None):
        self.location = location
        super().__init__(value)

    def __eq__(self, other):
        if isinstance(other, dict):
            return super().__eq__(other)
        if not isinstance(other, Dict):
            return False
        return super().__eq__(other) and self.location == other.location

    def __str__(self):
        return f"{self.__class__.__name__}({self!r}, location={self.location})"
