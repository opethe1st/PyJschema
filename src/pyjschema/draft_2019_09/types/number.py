import numbers

from pyjschema.common import Keyword

from pyjschema.utils import validate_only, basic_output


class _MultipleOf(Keyword):
    keyword = "multipleOf"

    @basic_output(error_message="{instance!r} is not a multiple of {value!r}")
    @validate_only(type_=(int, numbers.Number))
    def __call__(self, instance, location=None):
        # using this multipier here so that the precision is better
        multiplier = 100000
        instance = instance * multiplier
        value = self.value * multiplier
        if (instance % value) != 0:
            return False
        return True


class _Minimum(Keyword):
    keyword = "minimum"

    @basic_output("{instance!r} is less than {value!r}")
    @validate_only(type_=(int, numbers.Number))
    def __call__(self, instance, location=None):
        return self.value <= instance


class _Maximum(Keyword):
    keyword = "maximum"

    @basic_output("{instance!r} is more than {value!r}")
    @validate_only(type_=(int, numbers.Number))
    def __call__(self, instance, location=None):
        return instance <= self.value


class _ExclusiveMinimum(Keyword):
    keyword = "exclusiveMinimum"

    @basic_output("{instance!r} is more than or equal to {value!r}")
    @validate_only(type_=(int, numbers.Number))
    def __call__(self, instance, location=None):
        return self.value < instance


class _ExclusiveMaximum(Keyword):
    keyword = "exclusiveMaximum"

    @basic_output("{instance!r} is less than or equal to {value!r}")
    @validate_only(type_=(int, numbers.Number))
    def __call__(self, instance, location=None):
        return instance < self.value
