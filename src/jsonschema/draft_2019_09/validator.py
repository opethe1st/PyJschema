import typing as t

from jsonschema.common import (
    AValidator,
    Ref,
    Schema,
    ValidationResult,
    add_context_to_ref_validators,
    generate_context
)

from .array import Array
from .defs import Defs
from .number import Integer, Number
from .object_ import Object
from .primitives import AcceptAll, Boolean, Const, Enum, Null, RejectAll
from .string import String

__all__ = ["validate_once", "build_validator", "Validator"]


def validate_once(schema: t.Union[dict, bool], instance: dict) -> ValidationResult:
    validator = build_validator(schema)
    context = generate_context(validator)
    add_context_to_ref_validators(validator, context)
    return validator.validate(instance)


SCHEMA_TO_TYPE_VALIDATORS: t.Dict[str, t.Type[AValidator]] = {
    "string": String,
    "number": Number,
    "integer": Integer,
    "boolean": Boolean,
    "null": Null,
    "array": Array,
    "object": Object,
}


BuildValidatorReturns = t.Union[AcceptAll, RejectAll, "Validator", Ref]


def build_validator(schema: t.Union[Schema, bool]) -> BuildValidatorReturns:
    if schema is True or schema == {}:
        return AcceptAll()
    elif schema is False:
        return RejectAll()
    elif not isinstance(schema, dict):
        raise Exception("schema must be either a boolean or a dictionary")

    if "$ref" in schema:
        return Ref(ref=schema["$ref"])

    validator = Validator()

    if "$anchor" in schema:
        validator.anchor = "#" + schema["$anchor"]

    if "const" in schema:
        validator.add_validator(Const(const=schema["const"]))

    if "enum" in schema:
        validator.add_validator(Enum(enum=schema["enum"]))

    if "$defs" in schema:
        validator.add_validator(Defs(defs=schema["$defs"]))

    if "type" in schema:
        if isinstance(schema["type"], list):
            for type_ in schema["type"]:
                if type_ in SCHEMA_TO_TYPE_VALIDATORS:
                    validator.add_validator(
                        SCHEMA_TO_TYPE_VALIDATORS[type_](schema=schema)
                    )
        else:
            if schema["type"] in SCHEMA_TO_TYPE_VALIDATORS:
                validator.add_validator(
                    SCHEMA_TO_TYPE_VALIDATORS[schema["type"]](schema=schema)
                )

    return validator


class Validator(AValidator):
    def __init__(self):
        self.anchor = None
        self._validators = []

    def add_validator(self, validator: AValidator):
        self._validators.append(validator)

    # hm.. this is the same as the method in Type.
    def validate(self, instance):
        results = []
        for validator in self._validators:
            result = validator.validate(instance)

            if not result.ok:
                results.append(result)

        if not results:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(
                ok=False,
                messages=["error while validating this instance"],
                children=results,
            )

    # hm.. this is the same as the method in Type.
    def subschema_validators(self):
        for validator in self._validators:
            yield validator
