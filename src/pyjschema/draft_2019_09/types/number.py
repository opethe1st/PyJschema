import numbers

from pyjschema.common import Keyword

from pyjschema.utils import validate_only, ValidationResult


class _MultipleOf(Keyword):
    keyword = "multipleOf"

    @validate_only(type_=(int, numbers.Number))
    def __call__(self, instance, location):
        # using this multipier here so that the precision is better
        multiplier = 100000
        instance = instance * multiplier
        value = self.value * multiplier
        if (instance % value) != 0:
            return ValidationResult(
                message=f"{instance!r} is not a multiple of {self.value!r}",
                location=location,
                keywordLocation=self.location,
            )
        return True


class _Minimum(Keyword):
    keyword = "minimum"

    @validate_only(type_=(int, numbers.Number))
    def __call__(self, instance, location):
        res = self.value <= instance
        return (
            True
            if res
            else ValidationResult(
                message=f"{instance!r} is less than {self.value!r}",
                keywordLocation=self.location,
                location=location,
            )
        )


class _Maximum(Keyword):
    keyword = "maximum"

    @validate_only(type_=(int, numbers.Number))
    def __call__(self, instance, location):
        res = instance <= self.value
        return (
            True
            if res
            else ValidationResult(
                message=f"{instance!r} is more than {self.value!r}",
                keywordLocation=self.location,
                location=location,
            )
        )


class _ExclusiveMinimum(Keyword):
    keyword = "exclusiveMinimum"

    @validate_only(type_=(int, numbers.Number))
    def __call__(self, instance, location):
        res = self.value < instance
        return (
            True
            if res
            else ValidationResult(
                message=f"{instance!r} is more than or equal to {self.value!r}",
                keywordLocation=self.location,
                location=location,
            )
        )


class _ExclusiveMaximum(Keyword):
    keyword = "exclusiveMaximum"

    @validate_only(type_=(int, numbers.Number))
    def __call__(self, instance, location):
        res = instance < self.value
        return (
            True
            if res
            else ValidationResult(
                message=f"{instance!r} is less than or equal to {self.value!r}",
                keywordLocation=self.location,
                location=location,
            )
        )
