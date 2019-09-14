import dataclasses
import typing


@dataclasses.dataclass
class ValidationResult:
    ok: bool
    messages: typing.List[str] = dataclasses.field(default_factory=list)
    children: typing.List['ValidationResult'] = dataclasses.field(default_factory=list)
