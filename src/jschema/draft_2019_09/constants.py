import typing as t

from jschema.common import AValidator
from jschema.draft_2019_09.referencing import Ref

from .boolean_applicators import AllOf, AnyOf, If, Not, OneOf
from .defs import Defs
from .types import (
    Array,
    Boolean,
    Const,
    Enum,
    Integer,
    Null,
    Number,
    Object,
    String
)

TYPE_TO_TYPE_VALIDATORS: t.Dict[str, t.Type[AValidator]] = {
    "string": String,
    "number": Number,
    "integer": Integer,
    "boolean": Boolean,
    "null": Null,
    "array": Array,
    "object": Object,
}


KEYWORDS_TO_VALIDATOR: t.Dict[str, t.Type[AValidator]] = {
    "$ref": Ref,
    "const": Const,
    "enum": Enum,
    "$defs": Defs,
    "if": If,
    "allOf": AllOf,
    "anyOf": AnyOf,
    "oneOf": OneOf,
    "not": Not,
}
