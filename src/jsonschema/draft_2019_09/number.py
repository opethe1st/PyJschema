import numbers

from jsonschema.common import AValidator, ValidationResult


class MultipleOf(AValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if (instance % self.value) != 0:
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class Minimum(AValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if instance < self.value:
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class Maximum(AValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if self.value < instance:
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class ExclusiveMinimum(AValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if instance <= self.value:
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class ExclusiveMaximum(AValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if self.value <= instance:
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class NumberOrInteger(AValidator):
    def __init__(self, **kwargs):
        self.anchor = None
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
        for validator in self._validators:
            result = validator.validate(instance)
            if not result.ok:
                results.append(result)

        if not results:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(
                ok=False,
                children=results
            )


class Number(NumberOrInteger):

    def validate(self, instance):
        res = super().validate(instance=instance)
        if not isinstance(instance, numbers.Number):
            res.ok = False
            res.messages.append('instance is not a number')
        return res


class Integer(NumberOrInteger):

    def validate(self, instance):
        res = super().validate(instance=instance)
        if not isinstance(instance, int):
            res.ok = False
            res.messages.append('instance is not an integer')
        return res
