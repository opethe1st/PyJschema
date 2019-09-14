import typing

from jsonschema.common import ValidationResult

from .i_validator import AValidator
from .number import Number
from .primitives import AcceptAll, Boolean, Null, RejectAll
from .string import String
from .utils import Min, Max
# TODO(ope): rename this file to composite validation? or just composite?


class Const(AValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if instance == self.value:
            return ValidationResult(ok=True)
        else:
            # TODO I should add message
            return ValidationResult(ok=False)


class Enum(AValidator):
    def __init__(self, values):
        self.values = values

    def validate(self, instance):
        if instance in self.values:
            return ValidationResult(ok=True)
        else:
            # TODO I should add message
            return ValidationResult(ok=False)


class ItemsArray(AValidator):
    def __init__(self, items, additionalItems=None, **kwargs):
        self.item_validators = [build_validator(value) for value in items]
        self.additional_item_validator = build_validator(additionalItems) if additionalItems else None

    def validate(self, instance):
        children = []
        ok = True

        i = 0
        while i < len(self.item_validators):
            if i >= len(instance):
                break

            res = self.item_validators[i].validate(instance[i])
            if not res.ok:
                ok = False
                children.append(res)
            i += 1

        # additionalItem for the rest of the items in the instance
        if self.additional_item_validator:
            while i < len(instance):
                res = self.additional_item_validator.validate(instance[i])
                if not res.ok:
                    ok = False
                    children.append(res)
                i += 1

        return ValidationResult(ok=ok, children=children)


class Items(AValidator):
    def __init__(self, items, **kwargs):
        self._validator = build_validator(items)

    # TODO (ope) - stop using this ok = False pattern
    def validate(self, instance):
        children = []
        ok = True

        for value in instance:
            res = self._validator.validate(value)

            if not res.ok:
                ok = False
                children.append(res)

        return ValidationResult(ok=ok, children=children)


class Contains(AValidator):
    def __init__(self, value, **kwargs):
        self._validator = build_validator(value)

    # TODO(ope): stop using this ok = False pattern
    def validate(self, instance):
        ok = False

        for value in instance:
            res = self._validator.validate(value)

            if res.ok:
                ok = True

        if ok:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(
                ok=False,
                messages=["No item in this array matches the schema in the contains keyword"]
            )


class MinItems(AValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if len(instance) < self.value:
            return ValidationResult(ok=False, messages=[])
        return ValidationResult(ok=True)


class MaxItems(AValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if self.value < len(instance):
            return ValidationResult(ok=False, messages=[])

        return ValidationResult(ok=True)


class UniqueItems(AValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if self.value:
            itemsset = set([str(value) for value in instance])

            if len(itemsset) != len(instance):
                return ValidationResult(ok=False)

        return ValidationResult(ok=True)


class Array(AValidator):

    keyword_to_validator = {
        'minItems': MinItems,
        'maxItems': MaxItems,
        'uniqueItems': UniqueItems,
        'contains': Contains,
    }

    def __init__(self, **kwargs):
        self._validators = []

        for keyword in self.keyword_to_validator:

            if kwargs.get(keyword) is not None:
                self._validators.append(
                    self.keyword_to_validator[keyword](value=kwargs.get(keyword))
                )

        if 'items' in kwargs:

            if isinstance(kwargs['items'], list):
                items_validator = ItemsArray(items=kwargs['items'], additionalItems=kwargs.get('additionalItems'))
            else:
                items_validator = Items(items=kwargs['items'])
            self._validators.append(items_validator)

    def validate(self, instance):
        results = []
        messages = []

        if not isinstance(instance, list):
            messages.append('instance is not a number')
        for validator in self._validators:
            result = validator.validate(instance)

            if not result.ok:
                results.append(result)

        if not results and not messages:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(
                ok=False,
                messages=messages,
                children=results
            )


class Property(AValidator):

    def __init__(self, value=None, additionalProperties=None, patternProperties=None):
        import re
        self._validators = {key: build_validator(value) for key, value in value.items()} if value else {}
        self._additional_validator = build_validator(additionalProperties) if additionalProperties is not None else None
        self._pattern_validators = {
            re.compile(key): build_validator(value) for key, value in patternProperties.items()
        } if patternProperties else {}

    def validate(self, instance):
        results = []
        messages = []

        for key in self._validators:
            if key in instance:
                result = self._validators[key].validate(instance[key])

                if not result.ok:
                    results.append(result)

        additionalProperties = set(instance.keys()) - set(self._validators.keys())

        properties_validated_by_pattern = set()
        for regex in self._pattern_validators:
            for key in additionalProperties:
                if regex.match(key):
                    properties_validated_by_pattern.add(key)
                    result = self._pattern_validators[regex].validate(instance[key])
                    if not result.ok:
                        results.append(result)

        # additionalProperties only applies to properties not in properties or patternProperties
        additionalProperties -= properties_validated_by_pattern
        if self._additional_validator:
            for key in additionalProperties:
                result = self._additional_validator.validate(instance[key])
                if not result.ok:
                    results.append(result)

        if not results and not messages:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(
                ok=False,
                messages=messages,
                children=results
            )


class Required(AValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        messages = []
        if (set(self.value) - set(instance.keys())):
            messages.append(f"There are some missing required fields: {set(self.value) - set(instance.keys())}")

        if not messages:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(ok=False, messages=messages)


class PropertyNames(AValidator):
    # TODO(ope) rename to value to schema whenever a schema is expected.
    # need to change this line below to - self.keyword_to_validator[keyword](value=kwargs.get(keyword))
    # to self.keyword_to_validator[keyword](kwargs.get(keyword)) pass by position since the keyword args
    # might be different
    def __init__(self, value):
        # add this to make sure that the type is string - I have seen it missing from
        # examples in the documentation so can only assume it's allowed
        value["type"] = "string"
        self._validator = build_validator(value)

    def validate(self, instance):
        children = []
        for propertyName in instance:
            res = self._validator.validate(propertyName)

            if not res.ok:
                children.append(res)

        if not children:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(ok=False, children=children)


class MinProperties(Min):
    pass


class MaxProperties(Max):
    pass


class Object(AValidator):
    keyword_to_validator = {
        "required": Required,
        "propertyNames": PropertyNames,
        "minProperties": MinProperties,
        "maxProperties": MaxProperties,
    }

    def __init__(self, **kwargs):
        self._validators = []
        for keyword in self.keyword_to_validator:

            if kwargs.get(keyword) is not None:
                self._validators.append(
                    self.keyword_to_validator[keyword](value=kwargs.get(keyword))
                )

        if (
            kwargs.get("properties") is not None
            or kwargs.get("patternProperties") is not None
            or kwargs.get("additionalProperties") is not None
        ):
            self._validators.append(
                Property(
                    value=kwargs.get("properties"),
                    additionalProperties=kwargs.get("additionalProperties"),
                    patternProperties=kwargs.get("patternProperties")
                )
            )

    def validate(self, instance):
        results = []
        messages = []
        if not isinstance(instance, dict):
            messages.append('instance is not a dictionary')

        keyTypes = set(type(key) for key in instance)
        if keyTypes:
            if len(keyTypes) != 1 or not (str in keyTypes):
                messages.append('all the keys of the object need to be strings')

        for validator in self._validators:
            result = validator.validate(instance)

            if not result.ok:
                results.append(result)

        if not results and not messages:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(
                ok=False,
                messages=messages,
                children=results
            )


# TODO(ope); rename this to Validator?
class InstanceValidator(AValidator):

    def __init__(self):
        self._validators = []

    def add_validator(self, validator):
        self._validators.append(validator)

    def validate(self, instance) -> ValidationResult:
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


def build_validator(schema: typing.Union[dict, bool]) -> AValidator:
    if schema is True or schema == {}:
        return AcceptAll()
    elif schema is False:
        return RejectAll()
    if not isinstance(schema, dict):
        raise Exception("schema must be either a boolean or a dictionary")

    instance_validator = InstanceValidator()
    if 'const' in schema:
        instance_validator.add_validator(Const(value=schema['const']))
    if 'enum' in schema:
        instance_validator.add_validator(Enum(values=schema['enum']))
    if 'type' in schema:
        schema_type_to_validator: typing.Dict[str, typing.Type[AValidator]] = {
            'string': String,
            'number': Number,
            'boolean': Boolean,
            'null': Null,
            "array": Array,
            "object": Object
        }

        if schema['type'] in schema_type_to_validator:
            instance_validator.add_validator(
                schema_type_to_validator[schema['type']](**schema)
            )

    return instance_validator


# TODO(ope); add validate_once that's a convenient function
# def validate_once(schema, instance):
#     validator = build_validator(schema)
#     return validator.validate(instance)
