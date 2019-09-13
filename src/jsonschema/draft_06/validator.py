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
        return ValidationResult(ok=ok)


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


def build_validator(schema: dict) -> IValidator:
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
            'null': NullValidator
        }

        if schema['type'] in schema_type_to_validator:
            instance_validator.add_validator(
                schema_type_to_validator[schema['type']](**schema)
            )

    return instance_validator
