import dataclasses
import typing as t


@dataclasses.dataclass
class ValidationResult:
    ok: bool
    messages: t.List[str] = dataclasses.field(default_factory=list)
    children: t.List["ValidationResult"] = dataclasses.field(default_factory=list)
