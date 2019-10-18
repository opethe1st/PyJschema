import numbers

from jsonschema.common import Keyword, Type, ValidationResult


class _MultipleOf(Keyword):
    def __init__(self, multipleOf: int):
        self.value = multipleOf

    def validate(self, instance):
        if (instance % self.value) != 0:
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class _Minimum(Keyword):
    def __init__(self, minimum: int):
        self.value = minimum

    def validate(self, instance):
        if instance < self.value:
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class _Maximum(Keyword):
    def __init__(self, maximum: int):
        self.value = maximum

    def validate(self, instance):
        if self.value < instance:
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class _ExclusiveMinimum(Keyword):
    def __init__(self, exclusiveMinimum: int):
        self.value = exclusiveMinimum

    def validate(self, instance):
        if instance <= self.value:
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class _ExclusiveMaximum(Keyword):
    def __init__(self, exclusiveMaximum: int):
        self.value = exclusiveMaximum

    def validate(self, instance):
        if self.value <= instance:
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class _NumberOrInteger(Type):
    KEYWORDS_TO_VALIDATOR = {
        ("multipleOf",): _MultipleOf,
        ("minimum",): _Minimum,
        ("maximum",): _Maximum,
        ("exclusiveMinimum",): _ExclusiveMinimum,
        ("exclusiveMaximum",): _ExclusiveMaximum,
    }


class Number(_NumberOrInteger):
    type_ = numbers.Number


class Integer(_NumberOrInteger):
    type_ = int
