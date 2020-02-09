import numbers

from pyjschema.common import KeywordGroup, ValidationError

from .common import correct_type


class _MultipleOf(KeywordGroup):
    def __init__(self, schema: dict, location=None):
        super().__init__(schema=schema, location=location)
        self.value = schema["multipleOf"]

    @correct_type(type_=(int, numbers.Number))
    def validate(self, instance):
        # using this multipier here so that the precision is better
        multiplier = 100000
        instance = instance * multiplier
        value = self.value * multiplier
        if (instance % value) != 0:
            return ValidationError()
        return True


class _Minimum(KeywordGroup):
    def __init__(self, schema: dict, location=None):
        super().__init__(schema=schema, location=location)
        self.value = schema["minimum"]

    @correct_type(type_=(int, numbers.Number))
    def validate(self, instance):
        if instance < self.value:
            return ValidationError()
        return True


class _Maximum(KeywordGroup):
    def __init__(self, schema: dict, location=None):
        super().__init__(schema=schema, location=location)
        self.value = schema["maximum"]

    @correct_type(type_=(int, numbers.Number))
    def validate(self, instance):
        if self.value < instance:
            return ValidationError()
        return True


class _ExclusiveMinimum(KeywordGroup):
    def __init__(self, schema: dict, location=None):
        super().__init__(schema=schema, location=location)
        self.value = schema["exclusiveMinimum"]

    @correct_type(type_=(int, numbers.Number))
    def validate(self, instance):
        if instance <= self.value:
            return ValidationError()
        return True


class _ExclusiveMaximum(KeywordGroup):
    def __init__(self, schema: dict, location=None):
        super().__init__(schema=schema, location=location)
        self.value = schema["exclusiveMaximum"]

    @correct_type(type_=(int, numbers.Number))
    def validate(self, instance):
        if self.value <= instance:
            return ValidationError()
        return True
