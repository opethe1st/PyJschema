import abc
import collections.abc as ca
import numbers
import typing

from jsonschema.common import ValidationResult


JsonType = typing.Union[str, numbers.Number, bool, None, ca.Mapping, ca.Sequence]


class IValidator(abc.ABC):

    @abc.abstractmethod
    def __init__(self, **kwargs):
        pass

    @abc.abstractmethod
    def validate(self, instance: JsonType) -> ValidationResult:
        pass


class InstanceValidator(IValidator):

    def __init__(self):
        self._sub_validators = []

    def add_validator(self, validator):
        self._sub_validators.append(validator)

    def validate(self, instance) -> ValidationResult:
        results = []
        for validator in self._sub_validators:
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


class ConstValidator(IValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if instance == self.value:
            return ValidationResult(ok=True)
        else:
            # I should add message
            return ValidationResult(ok=False)


class EnumValidator(IValidator):
    def __init__(self, values):
        self.values = values

    def validate(self, instance):
        if instance in self.values:
            return ValidationResult(ok=True)
        else:
            # I should add message
            return ValidationResult(ok=False)


class StringValidator(IValidator):
    def __init__(self, **kwargs):
        self.minLength = kwargs.get('minLength')
        self.maxLength = kwargs.get('maxLength')
        self.pattern = kwargs.get('pattern')

    def validate(self, instance):
        messages = []
        ok = True
        if not isinstance(instance, str):
            messages.append('instance is not a string')
            ok = False
        if self.minLength:
            if len(instance) < self.minLength:
                messages.append('instance is too short')
                ok = False
        if self.maxLength:
            if self.maxLength < len(instance):
                messages.append('instance is too long')
                ok = False
        if self.pattern:
            import re
            if not re.match(self.pattern, instance):
                messages.append("instance doesn't match the pattern given")
                ok = False
        return ValidationResult(ok=ok, messages=messages)


class NumberValidator(IValidator):
    def __init__(self, **kwargs):
        self.multipleOf = kwargs.get('multipleOf')
        self.maximum = kwargs.get('maximum')
        self.exclusiveMaximum = kwargs.get('exclusiveMaximum')
        self.minimum = kwargs.get('minimum')
        self.exclusiveMinimum = kwargs.get('exclusiveMinimum')

    def validate(self, instance):
        messages = []
        ok = True
        if not isinstance(instance, numbers.Number):
            messages.append('instance is not a number')
            ok = False
        if self.multipleOf:
            if (instance % self.multipleOf) != 0:
                ok = False
                messages.append(f"This instance: {instance} is not a multipleOf {self.multipleOf}")
        if self.maximum:
            if self.maximum < instance:
                ok = False
                messages.append(f'This instance: {instance} is more than the maximum: {self.maximum}')
        if self.exclusiveMaximum:
            if self.exclusiveMaximum <= instance:
                ok = False
                messages.append(f'This instance: {instance} is more than or equal the exclusiveMaximum: {self.maximum}')
        if self.minimum:
            if instance < self.minimum:
                ok = False
                messages.append(f'this instance: {instance} is less than the minimum: {self.minimum}')
        if self.exclusiveMinimum:
            if instance <= self.exclusiveMinimum:
                ok = False
                messages.append(f'this instance: {instance} is less than or equal to the exclusiveMinimum: {self.exclusiveMinimum}')

        return ValidationResult(ok=ok, messages=messages)


class BooleanValidator(IValidator):
    def __init__(self, **kwargs):
        pass

    def validate(self, instance):
        # is this faster than an isinstance check?
        if (instance is True) or (instance is False):
            return ValidationResult(ok=True)
        else:
            return ValidationResult(ok=False, messages=['instance is not a valid boolean'])


class NullValidator(IValidator):
    def __init__(self, **kwargs):
        pass

    def validate(self, instance):
        if instance is None:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(ok=False)


class ItemsArrayValidator(IValidator):
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


class ItemsValidator(IValidator):
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


class ContainsValidator(IValidator):
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


class ArrayValidator(IValidator):
    def __init__(self, **kwargs):
        self.items_validator = None
        if 'items' in kwargs:
            if isinstance(kwargs['items'], list):
                self.items_validator = ItemsArrayValidator(items=kwargs['items'], additionalItems=kwargs.get('additionalItems'))
            else:
                self.items_validator = ItemsValidator(items=kwargs['items'])
        self.minItems = None
        if 'minItems' in kwargs:
            self.minItems = kwargs.pop('minItems')

        self.maxItems = None
        if 'maxItems' in kwargs:
            # does modifying like this lead to weird side-effects?
            self.maxItems = kwargs.pop('maxItems')

        self.uniqueItems = None
        if 'uniqueItems' in kwargs:
            # should probably make this, such that if not true, no need to save.
            self.uniqueItems = kwargs.pop('uniqueItems')
        # TODO(ope) - add support for the contains keyword
        self.contains_validator = None
        if 'contains' in kwargs:
            self.contains_validator = ContainsValidator(value=kwargs.pop('contains'))

    def validate(self, instance):
        messages = []
        children = []
        ok = True
        if not isinstance(instance, list):
            ok = False
            messages.append("instance is not an instance of a list")

        if self.items_validator:
            res = self.items_validator.validate(instance)
            if not res.ok:
                ok = False
                children.append(res)
        if self.minItems:
            if len(instance) < self.minItems:
                ok = False
                messages.append(f"length {len(instance)} is less than minItems {self.minItems}")
        if self.maxItems:
            if self.maxItems < len(instance):
                ok = False
                messages.append(f"length {len(instance)} is greater than maxItems {self.maxItems}")

        if self.uniqueItems:
            # this should work well enough I think but who knows
            itemsset = set([str(value) for value in instance])
            if len(itemsset) != len(instance):
                ok = False
                messages.append(f"Not all items in this instance: {instance} are unique")

        if self.contains_validator:
            res = self.contains_validator.validate(instance)
            if not res.ok:
                ok = False
                children.append(res)

        return ValidationResult(ok=ok, messages=messages, children=children)


class AcceptAllValidator(IValidator):
    def __init__(self, **kwargs):
        pass

    def validate(self, instance):
        return ValidationResult(ok=True)


class RejectAllValidator(IValidator):
    def __init__(self, **kwargs):
        pass

    def validate(self, instance):
        return ValidationResult(ok=False, messages=["This fails for every value"])


def build_validator(schema: typing.Union[dict, bool]) -> IValidator:
    if schema is True or schema == {}:
        return AcceptAllValidator()
    elif schema is False:
        return RejectAllValidator()
    if not isinstance(schema, dict):
        raise Exception("schema must be either a boolean or a dictionary")

    instance_validator = InstanceValidator()
    if 'const' in schema:
        instance_validator.add_validator(ConstValidator(value=schema['const']))
    if 'enum' in schema:
        instance_validator.add_validator(EnumValidator(values=schema['enum']))
    if 'type' in schema:
        schema_type_to_validator: typing.Dict[str, typing.Type[IValidator]] = {
            'string': StringValidator,
            'number': NumberValidator,
            'boolean': BooleanValidator,
            'null': NullValidator,
            "array": ArrayValidator,
        }

        if schema['type'] in schema_type_to_validator:
            instance_validator.add_validator(
                schema_type_to_validator[schema['type']](**schema)
            )

    return instance_validator
