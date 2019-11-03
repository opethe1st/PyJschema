import numbers

from jsonschema.common import Instance, Keyword, Type, ValidationResult


class _MultipleOf(Keyword):
    def __init__(self, multipleOf: Instance):
        self.value = multipleOf.value

    def validate(self, instance):
        multiplier = 100000
        instance = instance * multiplier
        value = self.value * multiplier
        if (instance % value) != 0:
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class _Minimum(Keyword):
    def __init__(self, minimum: Instance):
        self.value = minimum.value

    def validate(self, instance):
        if instance < self.value:
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class _Maximum(Keyword):
    def __init__(self, maximum: Instance):
        self.value = maximum.value

    def validate(self, instance):
        if self.value < instance:
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class _ExclusiveMinimum(Keyword):
    def __init__(self, exclusiveMinimum: Instance):
        self.value = exclusiveMinimum.value

    def validate(self, instance):
        if instance <= self.value:
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class _ExclusiveMaximum(Keyword):
    def __init__(self, exclusiveMaximum: Instance):
        self.value = exclusiveMaximum.value

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

    def validate(self, instance):
        results = []
        messages = []
        if self.type_ is not None and not isinstance(instance, self.type_):
            messages.append(f"instance is not a {self.type_}")

        if isinstance(instance, bool):
            messages.append(f"instance is not a {self.type_}")
        if messages:
            return ValidationResult(ok=False, messages=messages)

        results = list(
            filter(
                (lambda res: not res.ok),
                (validator.validate(instance) for validator in self._validators),
            )
        )

        if not results and not messages:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(ok=False, messages=messages, children=results)


class Number(_NumberOrInteger):
    type_ = numbers.Number


class Integer(_NumberOrInteger):
    type_ = int
