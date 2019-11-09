import typing as t

from jschema.common import Instance, ValidationResult
from jschema.common.annotate import annotate

from .constants import KEYWORDS_TO_VALIDATOR, TYPE_TO_TYPE_VALIDATORS
from .referencing import (
    Ref,
    add_context_to_ref_validators,
    attach_base_URIs,
    generate_context
)
from .types import AcceptAll, RejectAll
from .types_validator import Types
from .validator import Validator

__all__ = ["validate_once", "build_validator", "Validator"]


def construct_validator(schema):
    schema_validator = get_schema_validator(schema=schema)
    if schema_validator.validate(instance=schema).ok:
        validator, _ = build_validator_and_attach_context(schema=schema)
        return validator
    else:
        raise Exception("Schema is invalid according to the meta-schema")


def get_schema_validator(schema):
    # assume the schema is valid
    return AcceptAll()


def validate_once(schema: t.Union[dict, bool], instance: dict) -> ValidationResult:
    validator, _ = build_validator_and_attach_context(schema=schema)
    return validator.validate(instance=instance)


BuildValidatorResultType = t.Union[AcceptAll, RejectAll, "Validator", Ref]


def build_validator_and_attach_context(schema):
    schemaInstance = annotate(obj=schema)
    validator = build_validator(schema=schemaInstance)

    if isinstance(schemaInstance.value, dict):
        if "$id" in schemaInstance.value:
            attach_base_URIs(
                validator=validator, parent_URI=schemaInstance.value["$id"].value
            )
        else:
            # TODO(ope): properly fix this
            attach_base_URIs(
                validator=validator, parent_URI=""
            )
    context = generate_context(validator=validator)
    add_context_to_ref_validators(validator=validator, context=context)
    return validator, context


def build_validator(schema: Instance) -> BuildValidatorResultType:
    if schema.value is True or schema.value == {}:
        return AcceptAll()
    elif schema.value is False:
        return RejectAll()
    elif not isinstance(schema.value, dict):
        raise Exception("schema must be either a boolean or a dictionary")

    validator = Validator()

    for key, ValidatorClass in KEYWORDS_TO_VALIDATOR.items():
        if key in schema.value:
            validator.add_validator(ValidatorClass(schema=schema))

    validator.location = schema.location

    if "$anchor" in schema.value:
        validator.anchor = "#" + schema.value["$anchor"].value

    if "$id" in schema.value:
        validator.id = schema.value["$id"].value

    if "type" in schema.value:
        if isinstance(schema.value["type"].value, list):
            validator.add_validator(Types(schema=schema))
        else:
            if schema.value["type"].value in TYPE_TO_TYPE_VALIDATORS:
                validator.add_validator(
                    TYPE_TO_TYPE_VALIDATORS[schema.value["type"].value](schema=schema)
                )
    else:
        validator.add_validator(Types(schema=schema))

    return validator
