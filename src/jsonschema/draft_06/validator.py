import typing

from jsonschema.common import ValidationResult

from .i_validator import IValidator
from .number import Number
from .primitives import AcceptAll, Boolean, Null, RejectAll
from .string import String


class InstanceValidator(IValidator):

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


class Const(IValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if instance == self.value:
            return ValidationResult(ok=True)
        else:
            # TODO I should add message
            return ValidationResult(ok=False)


class Enum(IValidator):
    def __init__(self, values):
        self.values = values

    def validate(self, instance):
        if instance in self.values:
            return ValidationResult(ok=True)
        else:
            # TODO I should add message
            return ValidationResult(ok=False)


class ItemsArray(IValidator):
    def __init__(self, **kwargs):
        self.item_validators = [build_validator(value) for value in kwargs.get("items", [])]
        self.additional_item_validator = build_validator(kwargs['additionalItems']) if kwargs.get('additionalItems') else None

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


class Items(IValidator):
    def __init__(self, **kwargs):
        #  TODO should this be -> build_validator(kwargs["items"])
        self.values_validator = build_validator(kwargs.get("items"))

    def validate(self, instance):
        children = []
        ok = True
        for value in instance:
            res = self.values_validator.validate(value)
            if not res.ok:
                ok = False
                children.append(res)

        return ValidationResult(ok=ok, children=children)


class Contains(IValidator):
    def __init__(self, **kwargs):
        self.value_validator = build_validator(kwargs['value'])

    def validate(self, instance):
        ok = False
        for value in instance:
            res = self.value_validator.validate(value)
            if res.ok:
                ok = True
        if ok:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(ok=False, messages=["No item in this array matches the schema in the contains keyword"])


class MinItems(IValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if len(instance) < self.value:
            return ValidationResult(ok=False, messages=[])
        return ValidationResult(ok=True)


class MaxItems(IValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if self.value < len(instance):
            return ValidationResult(ok=False, messages=[])
        return ValidationResult(ok=True)


class UniqueItems(IValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if self.value:
            itemsset = set([str(value) for value in instance])
            if len(itemsset) != len(instance):
                return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class Array(IValidator):

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


def build_validator(schema: typing.Union[dict, bool]) -> IValidator:
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
        schema_type_to_validator: typing.Dict[str, typing.Type[IValidator]] = {
            'string': String,
            'number': Number,
            'boolean': Boolean,
            'null': Null,
            "array": Array,
        }

        if schema['type'] in schema_type_to_validator:
            instance_validator.add_validator(
                schema_type_to_validator[schema['type']](**schema)
            )

    return instance_validator
