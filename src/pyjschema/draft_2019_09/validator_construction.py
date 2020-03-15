import typing
from pyjschema.exceptions import SchemaError, ValidationError

from .context import BUILD_VALIDATOR, VOCABULARIES
from .referencing import resolve_references
from .types import AcceptAll, RejectAll
from .validator import Validator
from .vocabularies import METASCHEMA_VALIDATORS, get_vocabularies
from pyjschema.utils import SchemaLoader

__all__ = ["validate", "Validator", "construct_validator"]


def construct_validator(schema, check_schema=True):
    if check_schema:
        schema_validator = meta_schema_validator(schema=schema)
        # Need to wrap schema errors here and reraisr as SchemaErrors
        if not schema_validator(instance=schema):
            raise SchemaError(message="Schema is invalid according to the meta-schema")

    validator = build_validator_and_resolve_references(
        schema=schema,
        vocabularies=get_vocabularies(schema=schema),
        uri_to_validator={},
    )

    def validate(instance):
        # USE_SHORTCIRCUITING.set(True)
        return validator(instance=instance, location="/")

    return validate


def validate(
    schema: typing.Union[dict, bool],
    instance: dict,
    check_schema=False,
    raise_exceptions=False,
) -> bool:
    validate = construct_validator(schema=schema, check_schema=check_schema)
    res = validate(instance=instance)
    if not res and raise_exceptions:
        raise ValidationError(message="This instance doesnt conform to this schema")
    return res


def meta_schema_validator(schema):
    schema = schema if isinstance(schema, dict) else {}
    meta_schema = schema.get("$schema", "https://json-schema.org/draft/2019-09/schema")
    schemaLoader = SchemaLoader({"json-schema.org": "schemas/json_schema"})
    schema = schemaLoader.get(meta_schema)

    validator = build_validator_and_resolve_references(
        schema=schema, vocabularies=METASCHEMA_VALIDATORS, uri_to_validator={}
    )
    return validator


BuildValidatorResultType = typing.Union[AcceptAll, RejectAll, Validator]


def build_validator_and_resolve_references(schema, vocabularies, uri_to_validator):
    # challenge here is that contextvars is only supported by python 3.7 upwards
    VOCABULARIES.set(vocabularies)
    BUILD_VALIDATOR.set(build_validator)
    validator = build_validator(schema=schema, location="", parent=None)
    resolve_references(root_validator=validator, uri_to_validator=uri_to_validator)
    return validator


def build_validator(
    schema: typing.Union[bool, dict], location, parent
) -> BuildValidatorResultType:
    if isinstance(schema, dict):
        if schema.items():
            return Validator(schema=schema, location=location, parent=parent)
        else:
            return AcceptAll(schema=schema, location=location, parent=parent)
    elif isinstance(schema, (bool,)):
        if schema is True:
            return AcceptAll(schema=schema, location=location, parent=parent)
        else:
            return RejectAll(schema=schema, location=location, parent=parent)

    raise SchemaError(
        f"schema must be either a boolean or a dictionary. schema {schema}"
    )
