import numbers

from jsonschema.common import ValidationResult

from .i_validator import IValidator


# TODO move to it's own file
class MultipleOf(IValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if (instance % self.value) != 0:
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class Minimum(IValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if instance < self.value:
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class Maximum(IValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if self.value < instance:
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class ExclusiveMinimum(IValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if instance <= self.value:
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class ExclusiveMaximum(IValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if self.value <= instance:
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class Number(IValidator):
    def __init__(self, **kwargs):
        self._validators = []
        keyword_to_validator = {
            'multipleOf': MultipleOf,
            'minimum': Minimum,
            'maximum': Maximum,
            'exclusiveMinimum': ExclusiveMinimum,
            'exclusiveMaximum': ExclusiveMaximum,
        }
        for keyword in keyword_to_validator:
            if kwargs.get(keyword) is not None:
                self._validators.append(
                    keyword_to_validator[keyword](value=kwargs.get(keyword))
                )

    def validate(self, instance):
        results = []
        messages = []
        if not isinstance(instance, numbers.Number):
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
