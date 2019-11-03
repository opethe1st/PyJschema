import dataclasses as d
import typing as t


@d.dataclass
class Instance:
    value: t.Any
    location: str
