import numbers
from typing import Optional

from pyjschema.common import KeywordGroup, ValidationError

from .common import correct_type


class Primitive(KeywordGroup):
    keyword: Optional[str] = None

    def __init__(self, schema: dict, location=None, parent=None):
        if self.keyword is None:
            raise Exception("You need to provide a key to this function")
        self.value = schema[self.keyword]
        super().__init__(schema=schema, location=location, parent=parent)


class _MultipleOf(Primitive):
    keyword = "multipleOf"

    @correct_type(type_=(int, numbers.Number))
    def validate(self, instance):
        # using this multipier here so that the precision is better
        multiplier = 100000
        instance = instance * multiplier
        value = self.value * multiplier
        if (instance % value) != 0:
            return ValidationError()
        return True


class _Minimum(Primitive):
    keyword = "minimum"

    @correct_type(type_=(int, numbers.Number))
    def validate(self, instance):
        if instance < self.value:
            return ValidationError()
        return True


class _Maximum(Primitive):
    keyword = "maximum"

    @correct_type(type_=(int, numbers.Number))
    def validate(self, instance):
        if self.value < instance:
            return ValidationError()
        return True


class _ExclusiveMinimum(Primitive):
    keyword = "exclusiveMinimum"

    @correct_type(type_=(int, numbers.Number))
    def validate(self, instance):
        if instance <= self.value:
            return ValidationError()
        return True


class _ExclusiveMaximum(Primitive):
    keyword = "exclusiveMaximum"

    @correct_type(type_=(int, numbers.Number))
    def validate(self, instance):
        if self.value <= instance:
            return ValidationError()
        return True
