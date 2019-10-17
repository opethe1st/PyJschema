import typing

from jsonschema.common import AValidator, ValidationResult
from jsonschema.common.reference_resolver import (
    Ref,
    add_context_to_ref_validators,
    generate_context
)

from .array import Array
from .defs import Defs
from .number import Integer, Number
from .object_ import Object
from .primitives import AcceptAll, Boolean, Const, Enum, Null, RejectAll
from .string import String

__all__ = [
    'validate_once',
    'build_validator',
    'Validator',
]


def validate_once(schema: typing.Union[dict, bool], instance: dict) -> ValidationResult:
    validator = build_validator(schema)
    context = generate_context(validator)
    add_context_to_ref_validators(validator, context)
    return validator.validate(instance)


SCHEMA_TO_TYPE_VALIDATORS: typing.Dict[str, typing.Type[AValidator]] = {
    'string': String,
    'number': Number,
    'integer': Integer,
    'boolean': Boolean,
    'null': Null,
    "array": Array,
    "object": Object,
}


def build_validator(schema: typing.Union[dict, bool]) -> typing.Union[AcceptAll, RejectAll, "Validator", "Ref"]:
    if schema is True or schema == {}:
        return AcceptAll()
    elif schema is False:
        return RejectAll()
    elif not isinstance(schema, dict):
        raise Exception("schema must be either a boolean or a dictionary")

    if "$ref" in schema:
        return Ref(value=schema["$ref"])

    validator = Validator()

    if "$anchor" in schema:
        validator.anchor = "#" + schema["$anchor"]

    if 'const' in schema:
        validator.add_validator(Const(value=schema['const']))

    if 'enum' in schema:
        validator.add_validator(Enum(values=schema['enum']))

    if '$defs' in schema:
        validator.add_validator(Defs(definitions=schema['$defs']))

    if 'type' in schema:
        if schema['type'] in SCHEMA_TO_TYPE_VALIDATORS:
            validator.add_validator(
                SCHEMA_TO_TYPE_VALIDATORS[schema['type']](**schema)
            )

    return validator


class Validator(AValidator):

    def __init__(self):
        self.anchor = None
        self._validators = []

    def add_validator(self, validator: AValidator):
        self._validators.append(validator)

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
                children=results
            )

    def subschema_validators(self):
        for validator in self._validators:
            yield validator
