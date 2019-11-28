import json
import os
import typing as t

from jschema.common import Instance, Dict, ValidationResult
from jschema.common.annotate import annotate

from .referencing import (
    add_context_to_ref_validators,
    attach_base_URIs,
    generate_context,
)
from .types import AcceptAll, RejectAll
from .validator import Validator

__all__ = ["validate_once", "build_validator", "Validator"]


def construct_validator(schema):
    schema_validator = meta_schema_validator()

    if schema_validator.validate(instance=schema).ok:
        validator, _ = build_validator_and_attach_context(schema=schema)
        return validator
    else:
        raise Exception("Schema is invalid according to the meta-schema")


def meta_schema_validator():
    # assume the schema is valid
    base_dir = os.path.dirname(__file__)
    with open(os.path.join(base_dir, "validator-schema.json"), "r") as file:
        schema = json.load(file)
    validator, _ = build_validator_and_attach_context(schema)
    return validator


def validate_once(schema: t.Union[dict, bool], instance: dict) -> ValidationResult:
    validator, _ = build_validator_and_attach_context(schema=schema)
    return validator.validate(instance=instance)


BuildValidatorResultType = t.Union[AcceptAll, RejectAll, Validator]


def build_validator_and_attach_context(schema):
    schemaInstance = annotate(obj=schema)
    validator = build_validator(schema=schemaInstance)
    root_base_URI = ""
    if isinstance(schemaInstance, Dict):

        if "$id" in schemaInstance:
            root_base_URI = schemaInstance["$id"].value.rstrip("#")
            attach_base_URIs(validator=validator, parent_URI=root_base_URI)
        else:
            # TODO(ope): properly fix this
            attach_base_URIs(validator=validator, parent_URI="")

    context, base_uri_to_abs_location = generate_context(
        validator=validator, root_base_uri=root_base_URI
    )
    add_context_to_ref_validators(
        validator=validator,
        context=context,
        base_uri_to_abs_location=base_uri_to_abs_location,
    )
    return validator, context


def build_validator(schema: t.Union[Instance, Dict]) -> BuildValidatorResultType:
    if isinstance(schema, Dict):
        if schema.items():
            return Validator(schema=schema)
        else:
            return AcceptAll(schema=Instance(value=True, location=schema.location))
    elif isinstance(schema, Instance):
        if isinstance(schema.value, bool):
            if schema.value is True:
                return AcceptAll(schema=schema)
            elif schema.value is False:
                return RejectAll(schema=schema)
        else:
            raise Exception("schema must be either a boolean or a dictionary")
    else:
        raise Exception(f"schema needs to an instance of Instance or Dict, schema is {schema}")
    return AcceptAll(schema=Instance(value=True, location='#'))  # just to satisfy mypy
