from collections import ChainMap

from .boolean_applicators import AllOf, AnyOf, IfElseThen, Not, OneOf
from .defs import Defs
from .ref import RecursiveRef, Ref
from .types import Const, Enum
from .types.array import _Contains, _Items, _MaxItems, _MinItems, _UniqueItems
from .types.number import (
    _ExclusiveMaximum,
    _ExclusiveMinimum,
    _Maximum,
    _Minimum,
    _MultipleOf,
)
from .types.object_ import (
    _DependentRequired,
    _MaxProperties,
    _MinProperties,
    _Property,
    _PropertyNames,
    _Required,
)
from .types.string import _MaxLength, _MinLength, _Pattern
from .types.type_ import Type

CORE_VOCABULARY = {"$ref": Ref, "$recursiveRef": RecursiveRef, "$defs": Defs}

VALIDATOR_VOCABULARY = {
    "multipleOf": _MultipleOf,
    "maximum": _Maximum,
    "exclusiveMaximum": _ExclusiveMaximum,
    "minimum": _Minimum,
    "exclusiveMinimum": _ExclusiveMinimum,
    "maxLength": _MaxLength,
    "minLength": _MinLength,
    "pattern": _Pattern,
    "maxItems": _MaxItems,
    "minItems": _MinItems,
    "uniqueItems": _UniqueItems,
    "contains": _Contains,
    "maxContains": _Contains,
    "minContains": _Contains,
    "maxProperties": _MaxProperties,
    "minProperties": _MinProperties,
    "required": _Required,
    "dependentRequired": _DependentRequired,
    "const": Const,
    "enum": Enum,
    "type": Type,
}


APPLICATOR_VOCABULARY = {
    "items": _Items,
    "additionalItems": _Items,  # additionalItems only applies if items is defined
    "contains": _Contains,
    "additionalProperties": _Property,
    "properties": _Property,
    "patternProperties": _Property,
    "propertyNames": _PropertyNames,
    "if": IfElseThen,
    "then": IfElseThen,
    "else": IfElseThen,
    "allOf": AllOf,
    "anyOf": AnyOf,
    "oneOf": OneOf,
    "not": Not,
    # "dependentSchemas": DependentSchemas,
    # "unevaluatedItems": UnevaluatedItems,
    # "unevaluatedProperties": UnevaluatedProperties,
}


KEYWORD_TO_VALIDATOR = ChainMap(
    CORE_VOCABULARY, VALIDATOR_VOCABULARY, APPLICATOR_VOCABULARY
)
