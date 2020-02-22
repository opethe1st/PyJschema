import numbers

from pyjschema.common import ValidationError, Keyword

from .common import correct_type


class _MultipleOf(Keyword):
    keyword = "multipleOf"

    @correct_type(type_=(int, numbers.Number))
    def __call__(self, instance):
        # using this multipier here so that the precision is better
        multiplier = 100000
        instance = instance * multiplier
        value = self.value * multiplier
        if (instance % value) != 0:
            return ValidationError()
        return True


class _Minimum(Keyword):
    keyword = "minimum"

    @correct_type(type_=(int, numbers.Number))
    def __call__(self, instance):
        if instance < self.value:
            return ValidationError()
        return True


class _Maximum(Keyword):
    keyword = "maximum"

    @correct_type(type_=(int, numbers.Number))
    def __call__(self, instance):
        if self.value < instance:
            return ValidationError()
        return True


class _ExclusiveMinimum(Keyword):
    keyword = "exclusiveMinimum"

    @correct_type(type_=(int, numbers.Number))
    def __call__(self, instance):
        if instance <= self.value:
            return ValidationError()
        return True


class _ExclusiveMaximum(Keyword):
    keyword = "exclusiveMaximum"

    @correct_type(type_=(int, numbers.Number))
    def __call__(self, instance):
        if self.value <= instance:
            return ValidationError()
        return True
