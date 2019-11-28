import numbers

from jschema.common import Primitive, KeywordGroup, Type, ValidationResult


class _MultipleOf(KeywordGroup):
    def __init__(self, multipleOf: Primitive):
        self.value = multipleOf.value

    def validate(self, instance):
        # using this multipier here so that the precision is better
        multiplier = 100000
        instance = instance * multiplier
        value = self.value * multiplier
        if (instance % value) != 0:
            raise Exception
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class _Minimum(KeywordGroup):
    def __init__(self, minimum: Primitive):
        self.value = minimum.value

    def validate(self, instance):
        if instance < self.value:
            raise Exception
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class _Maximum(KeywordGroup):
    def __init__(self, maximum: Primitive):
        self.value = maximum.value

    def validate(self, instance):
        if self.value < instance:
            raise Exception
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class _ExclusiveMinimum(KeywordGroup):
    def __init__(self, exclusiveMinimum: Primitive):
        self.value = exclusiveMinimum.value

    def validate(self, instance):
        if instance <= self.value:
            raise Exception
            return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class _ExclusiveMaximum(KeywordGroup):
    def __init__(self, exclusiveMaximum: Primitive):
        self.value = exclusiveMaximum.value

    def validate(self, instance):
        if self.value <= instance:
            raise Exception
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
            messages.append(f"instance: {instance} is not a {self.type_}")

        if isinstance(instance, bool):
            messages.append(f"instance: {instance} is not a {self.type_}")
        if messages:
            raise Exception
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
            raise Exception
            return ValidationResult(ok=False, messages=messages, children=results)


class Number(_NumberOrInteger):
    type_ = numbers.Number


class Integer(_NumberOrInteger):
    type_ = int
