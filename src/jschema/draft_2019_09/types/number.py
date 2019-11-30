import itertools
import numbers

from jschema.common import KeywordGroup, Primitive, ValidationError

from .common import validate_instance_against_all_validators
from .type_base import Type


class _MultipleOf(KeywordGroup):
    def __init__(self, multipleOf: Primitive):
        self.value = multipleOf.value

    def validate(self, instance):
        # using this multipier here so that the precision is better
        multiplier = 100000
        instance = instance * multiplier
        value = self.value * multiplier
        if (instance % value) != 0:
            return ValidationError()
        return True


class _Minimum(KeywordGroup):
    def __init__(self, minimum: Primitive):
        self.value = minimum.value

    def validate(self, instance):
        if instance < self.value:
            return ValidationError()
        return True


class _Maximum(KeywordGroup):
    def __init__(self, maximum: Primitive):
        self.value = maximum.value

    def validate(self, instance):
        if self.value < instance:
            return ValidationError()
        return True


class _ExclusiveMinimum(KeywordGroup):
    def __init__(self, exclusiveMinimum: Primitive):
        self.value = exclusiveMinimum.value

    def validate(self, instance):
        if instance <= self.value:
            return ValidationError()
        return True


class _ExclusiveMaximum(KeywordGroup):
    def __init__(self, exclusiveMaximum: Primitive):
        self.value = exclusiveMaximum.value

    def validate(self, instance):
        if self.value <= instance:
            return ValidationError()
        return True


class _NumberOrInteger(Type):
    KEYWORDS_TO_VALIDATOR = {
        ("multipleOf",): _MultipleOf,
        ("minimum",): _Minimum,
        ("maximum",): _Maximum,
        ("exclusiveMinimum",): _ExclusiveMinimum,
        ("exclusiveMaximum",): _ExclusiveMaximum,
    }

    def validate(self, instance):
        messages = []
        if self.type_ is not None and not isinstance(instance, self.type_):
            messages.append(f"instance: {instance} is not a {self.type_}")

        # TODO: this looks weird to me. Needs a closer look
        if isinstance(instance, bool):
            messages.append(f"instance: {instance} is not a {self.type_}")
        if messages:
            return ValidationError(messages=messages)
        errors = validate_instance_against_all_validators(validators=self._validators, instance=instance)
        first_error = next(errors, True)
        if first_error and not messages:
            return True
        else:
            return ValidationError(messages=messages, children=itertools.chain([first_error], errors))


class Number(_NumberOrInteger):
    type_ = numbers.Number


class Integer(_NumberOrInteger):
    type_ = int
