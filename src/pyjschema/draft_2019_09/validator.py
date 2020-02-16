import itertools
import typing as t

from pyjschema.common import AValidator, ValidationError
from pyjschema.draft_2019_09.referencing import Ref

from .constants import KEYWORDS_TO_VALIDATOR
from .defs import Defs
from .types.common import validate_instance_against_all_validators
from .types.string import _MaxLength, _MinLength, _Pattern
from .types.number import _MultipleOf, _Minimum, _Maximum, _ExclusiveMinimum, _ExclusiveMaximum
from .types.object_ import _Property, _Required, _PropertyNames, _MinProperties, _MaxProperties, _DependentRequired
from .types.array import _Items, _Contains, _MinItems, _MaxItems, _UniqueItems
from .types.type_ import Type


# this should probably be in the files for each type
TYPE_TO_KEYWORD_VALIDATORS = {
    "string": {
        ("minLength",): _MinLength,
        ("maxLength",): _MaxLength,
        ("pattern",): _Pattern,
    },
    "integer": {
        ("multipleOf",): _MultipleOf,
        ("minimum",): _Minimum,
        ("maximum",): _Maximum,
        ("exclusiveMinimum",): _ExclusiveMinimum,
        ("exclusiveMaximum",): _ExclusiveMaximum,
    },
    "number": {
        ("multipleOf",): _MultipleOf,
        ("minimum",): _Minimum,
        ("maximum",): _Maximum,
        ("exclusiveMinimum",): _ExclusiveMinimum,
        ("exclusiveMaximum",): _ExclusiveMaximum,
    },
    "object": {
        ("required",): _Required,
        ("propertyNames",): _PropertyNames,
        ("minProperties",): _MinProperties,
        ("maxProperties",): _MaxProperties,
        ("dependentRequired",): _DependentRequired,
        ("properties", "patternProperties", "additionalProperties"): _Property,
    },
    "array": {
        ("minItems",): _MinItems,
        ("maxItems",): _MaxItems,
        ("uniqueItems",): _UniqueItems,
        ("contains", "maxContains", "minContains"): _Contains,
        ("items", "additionalItems"): _Items,
    },
}


class Validator(AValidator):
    """
    This corresponds to a schema
    """

    def __init__(self, schema, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        self._validators: t.List[AValidator] = []

        if "$recursiveAnchor" in schema:
            self.recursiveAnchor = schema.get("$recursiveAnchor", False)

        # need a reference to the parent. for this, then to evaluate
        if "$recursiveRef" in schema:
            self.recursiveRef = schema.get("$recursiveRef")

        if "$anchor" in schema:
            self.anchor = "#" + schema["$anchor"]

        if "$id" in schema:
            self.id = schema["$id"].rstrip("#")

        if "$defs" in schema:
            self._validators.append(Defs(schema=schema, location=f"{location}/$defs"))

        if "$ref" in schema:
            self._validators.append(Ref(schema=schema))

        for key, ValidatorClass in KEYWORDS_TO_VALIDATOR.items():
            if key in schema:
                self._validators.append(ValidatorClass(schema=schema, location=f"{location}/{key}"))

        types = schema.get("type")
        if isinstance(types, str):
            types = [types]
        if types:
            self._validators.append(Type(schema=schema))

        for type_, keyword_to_keyword_validators in TYPE_TO_KEYWORD_VALIDATORS.items():
            if not types or type_ in types:
                for keywords, KeywordValidator in keyword_to_keyword_validators.items():
                    if any(keyword in schema for keyword in keywords):
                        self._validators.append(KeywordValidator(schema=schema, location=location))

    def validate(self, instance):
        errors = validate_instance_against_all_validators(
            validators=self._validators, instance=instance
        )
        first_result = next(errors, True)
        if first_result:
            return True
        else:
            return ValidationError(
                messages=["error while validating this instance"],
                children=itertools.chain([first_result], errors),
            )

    def sub_validators(self):
        yield from self._validators

    def __repr__(self):
        return f"Validator(validators={self._validators})"
