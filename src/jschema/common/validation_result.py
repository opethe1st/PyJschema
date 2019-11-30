import typing as t

import dataclasses


@dataclasses.dataclass
class ValidationError:
    messages: t.List[str] = dataclasses.field(default_factory=list)
    children: t.Iterable["ValidationError"] = dataclasses.field(default_factory=list)

    def __bool__(self):
        return False
