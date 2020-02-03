import itertools
import numbers

from pyjschema.common import KeywordGroup, ValidationError, Dict

from .common import validate_instance_against_all_validators
from .type_ import Type


class _MultipleOf(KeywordGroup):
    def __init__(self, schema: Dict):
        super().__init__(schema=schema)
        self.value = schema["multipleOf"].value

    def validate(self, instance):
        # using this multipier here so that the precision is better
        multiplier = 100000
        instance = instance * multiplier
        value = self.value * multiplier
        if (instance % value) != 0:
            return ValidationError()
        return True


class _Minimum(KeywordGroup):
    def __init__(self, schema: Dict):
        super().__init__(schema=schema)
        self.value = schema["minimum"].value

    def validate(self, instance):
        if instance < self.value:
            return ValidationError()
        return True


class _Maximum(KeywordGroup):
    def __init__(self, schema: Dict):
        super().__init__(schema=schema)
        self.value = schema["maximum"].value

    def validate(self, instance):
        if self.value < instance:
            return ValidationError()
        return True


class _ExclusiveMinimum(KeywordGroup):
    def __init__(self, schema: Dict):
        super().__init__(schema=schema)
        self.value = schema["exclusiveMinimum"].value

    def validate(self, instance):
        if instance <= self.value:
            return ValidationError()
        return True


class _ExclusiveMaximum(KeywordGroup):
    def __init__(self, schema: Dict):
        super().__init__(schema=schema)
        self.value = schema["exclusiveMaximum"].value

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
        if self.type_ is not None:
            if isinstance(instance, bool):
                messages.append(f"instance: {instance} is not a {self.type_}")
            else:
                if not isinstance(instance, self.type_):
                    messages.append(f"instance: {instance} is not a {self.type_}")

        if messages:
            return ValidationError(messages=messages)
        errors = validate_instance_against_all_validators(
            validators=self._validators, instance=instance
        )
        first_result = next(errors, True)
        if first_result and not messages:
            return True
        else:
            return ValidationError(
                messages=messages, children=itertools.chain([first_result], errors)
            )


class Number(_NumberOrInteger):
    type_ = numbers.Number


class Integer(_NumberOrInteger):
    type_ = int
