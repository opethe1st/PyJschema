import dataclasses as d
import typing as t


@d.dataclass
class Instance:
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
        return f"List({self!r}, location={self.location})"


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
        return f"Dict({self!r}, location={self.location})"
