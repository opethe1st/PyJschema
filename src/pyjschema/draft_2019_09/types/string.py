from pyjschema.common import Keyword
from pyjschema.utils import validate_only, ValidationResult


class _MaxLength(Keyword):
    keyword = "maxLength"

    @validate_only(type_=str)
    def __call__(self, instance, location):
        res = len(instance) <= self.value
        return (
            True
            if res
            else ValidationResult(
                message=f"{instance!r}'s length is more than max_length: {self.value!r}",
                keywordLocation=self.location,
                location=location,
            )
        )


class _MinLength(Keyword):
    keyword = "minLength"

    @validate_only(type_=str)
    def __call__(self, instance, location):
        res = self.value <= len(instance)
        return (
            True
            if res
            else ValidationResult(
                message=f"{instance!r}'s length is less than min_length: {self.value!r}",
                keywordLocation=self.location,
                location=location,
            )
        )


class _Pattern(Keyword):
    keyword = "pattern"

    def __init__(self, schema: dict, location, parent):
        super().__init__(schema=schema, location=location, parent=parent)
        import re

        self.regex = re.compile(pattern=self.value)

    @validate_only(type_=str)
    def __call__(self, instance, location):
        if not self.regex.search(instance):
            return ValidationResult(
                message=f"{instance!r} doesnt match this pattern: {self.value!r}",
                location=location,
                keywordLocation=self.location,
            )
        return True
