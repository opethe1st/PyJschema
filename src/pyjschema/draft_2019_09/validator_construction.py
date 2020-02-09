import json
import os
import typing

from pyjschema.common import Dict, Primitive, ValidationError

from .exceptions import SchemaError
from .referencing import resolve_references
from .types import AcceptAll, RejectAll
from .validator import Validator

__all__ = ["validate_once", "Validator", "construct_validator"]


def construct_validator(schema):
    schema_validator = meta_schema_validator(schema=schema.get("$schema"))

    if schema_validator.validate(instance=schema):
        validator = build_validator_and_resolve_references(schema=schema)
        return validator
    else:
        raise Exception("Schema is invalid according to the meta-schema")


def validate_once(schema: typing.Union[dict, bool], instance: dict) -> ValidationError:
    validator = build_validator_and_resolve_references(schema=schema)
    return validator.validate(instance=instance)


def meta_schema_validator(schema):
    return AcceptAll(schema=schema or {})
    base_dir = os.path.dirname(__file__)
    with open(os.path.join(base_dir, "validator-schema.json"), "r") as file:
        schema = json.load(file)
    validator = build_validator_and_resolve_references(schema)
    return validator


BuildValidatorResultType = typing.Union[AcceptAll, RejectAll, Validator]


def build_validator_and_resolve_references(schema):
    schemaInstance = schema
    validator = build_validator(schema=schemaInstance)
    resolve_references(root_validator=validator)
    return validator


def build_validator(schema: typing.Union[Primitive, Dict], location="") -> BuildValidatorResultType:
    if isinstance(schema, dict):
        if schema.items():
            return Validator(schema=schema, location=location)
        else:
            return AcceptAll(location=location)
    elif isinstance(schema, (bool,)):
        if schema is True:
            return AcceptAll(location=location)
        elif schema is False:
            return RejectAll(location=location)

    # temp
    return RejectAll(location=location)
    raise SchemaError(f"schema must be either a boolean or a dictionary. schema {schema}")
