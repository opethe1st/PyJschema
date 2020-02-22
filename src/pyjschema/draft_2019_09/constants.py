import typing as t

from pyjschema.common import AValidator

from .boolean_applicators import AllOf, AnyOf, IfElseThen, Not, OneOf
from .types import Const, Enum

KEYWORDS_TO_VALIDATOR: t.Dict[str, t.Type[AValidator]] = {
    "const": Const,
    "enum": Enum,
    "if": IfElseThen,
    "allOf": AllOf,
    "anyOf": AnyOf,
    "oneOf": OneOf,
    "not": Not,
}
