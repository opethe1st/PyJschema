import typing as t

from jsonschema.common import (
    AValidator,
    Instance,
    Ref,
    Type,
    ValidationResult,
    add_context_to_ref_validators,
    attach_base_URIs,
    generate_context,
)
from jsonschema.common.annotate import annotate

from .boolean_applicators import If
from .defs import Defs
from .types import (
    AcceptAll,
    Array,
    Boolean,
    Const,
    Enum,
    Integer,
    Null,
    Number,
    Object,
    RejectAll,
    String,
)

__all__ = ["validate_once", "build_validator", "Validator"]


def validate_once(schema: t.Union[dict, bool], instance: dict) -> ValidationResult:
    schemaInstance = annotate(obj=schema)

    validator = build_validator(schema=schemaInstance)

    if isinstance(schemaInstance.value, dict):
        if "$id" in schemaInstance.value:
            attach_base_URIs(
                validator=validator, parent_URI=schemaInstance.value["$id"].value
            )
        else:
            raise Exception("The root schema needs to have $id defined")
    context = generate_context(validator=validator)
    add_context_to_ref_validators(validator=validator, context=context)
    return validator.validate(instance=instance)


SCHEMA_TO_TYPE_VALIDATORS: t.Dict[str, t.Type[AValidator]] = {
    "string": String,
    "number": Number,
    "integer": Integer,
    "boolean": Boolean,
    "null": Null,
    "array": Array,
    "object": Object,
}


BuildValidatorResultType = t.Union[AcceptAll, RejectAll, "Validator", Ref]


def build_validator(schema: Instance) -> BuildValidatorResultType:
    if schema.value is True or schema.value == {}:
        return AcceptAll()
    elif schema.value is False:
        return RejectAll()
    elif not isinstance(schema.value, dict):
        raise Exception("schema must be either a boolean or a dictionary")

    if "$ref" in schema.value:
        return Ref(ref=schema.value["$ref"])

    validator = Validator()

    if "$anchor" in schema.value:
        validator.anchor = "#" + schema.value["$anchor"].value

    if "const" in schema.value:
        validator.add_validator(Const(const=schema.value["const"]))

    if "enum" in schema.value:
        validator.add_validator(Enum(enum=schema.value["enum"]))

    if "$defs" in schema.value:
        validator.add_validator(Defs(defs=schema.value["$defs"]))

    if "$id" in schema.value:
        validator.id = schema.value["$id"].value

    if "if" in schema.value:
        validator.add_validator(If(schema=schema))

    if "type" in schema.value:
        if isinstance(schema.value["type"].value, list):
            validator.add_validator(Types(schema=schema))
        else:
            if schema.value["type"].value in SCHEMA_TO_TYPE_VALIDATORS:
                validator.add_validator(
                    SCHEMA_TO_TYPE_VALIDATORS[schema.value["type"].value](schema=schema)
                )
    else:
        validator.add_validator(Types(schema=schema))

    return validator


class Types(AValidator):
    def __init__(self, schema):
        self._validators = []
        if "type" in schema.value:
            types = [item.value for item in schema.value["type"].value]
        else:
            # if there is no type, then try all the types
            types = SCHEMA_TO_TYPE_VALIDATORS.keys()

        for type_ in types:
            if type_ in SCHEMA_TO_TYPE_VALIDATORS:
                self._validators.append(SCHEMA_TO_TYPE_VALIDATORS[type_](schema=schema))

    def validate(self, instance):
        results = []

        for validator in self._validators:
            result = validator.validate(instance)

            if result.ok:
                return result
            else:
                results.append(result)

        return ValidationResult(
            ok=False,
            messages=["error while validating this instance"],
            children=results,
        )


class Validator(AValidator):
    def __init__(self):
        self._validators: t.List[AValidator] = []

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


def all_keywords(type_cls):
    if issubclass(type_cls, Type):
        res = []
        for keywords in type_cls.KEYWORDS_TO_VALIDATOR.keys():
            res.extend(list(keywords))
        return set(res)
    return set()
