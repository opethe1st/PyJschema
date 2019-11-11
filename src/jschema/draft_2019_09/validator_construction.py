import typing as t

from jschema.common import Instance, ValidationResult
from jschema.common.annotate import annotate

from .referencing import (
    add_context_to_ref_validators,
    attach_base_URIs,
    generate_context
)
from .types import AcceptAll, RejectAll
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


BuildValidatorResultType = t.Union[AcceptAll, RejectAll, Validator]


def build_validator_and_attach_context(schema):
    schemaInstance = annotate(obj=schema)
    validator = build_validator(schema=schemaInstance)
    root_base_URI = ""
    if isinstance(schemaInstance.value, dict):

        if "$id" in schemaInstance.value:
            root_base_URI = schemaInstance.value["$id"].value.rstrip("#")
            attach_base_URIs(validator=validator, parent_URI=root_base_URI)
        else:
            # TODO(ope): properly fix this
            attach_base_URIs(validator=validator, parent_URI="")

    context = generate_context(validator=validator, root_base_uri=root_base_URI)
    add_context_to_ref_validators(validator=validator, context=context)
    return validator, context


def build_validator(schema: Instance) -> BuildValidatorResultType:
    if schema.value is True or schema.value == {}:
        return AcceptAll(schema=schema)
    elif schema.value is False:
        return RejectAll(schema=schema)
    elif not isinstance(schema.value, dict):
        # this should never happen
        raise Exception("schema must be either a boolean or a dictionary")
    else:
        return Validator(schema=schema)
