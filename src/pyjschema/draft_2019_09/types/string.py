from pyjschema.common import Keyword, ValidationError

from .common import validate_max, validate_min, correct_type


class _MaxLength(Keyword):
    keyword = "maxLength"

    @correct_type(type_=str)
    def __call__(self, instance):
        return validate_max(
            value=self.value, instance=instance, message=f"{instance} failed {self}"
        )


class _MinLength(Keyword):
    keyword = "minLength"

    @correct_type(type_=str)
    def __call__(self, instance):
        return validate_min(
            value=self.value, instance=instance, message=f"{instance} failed {self}"
        )


class _Pattern(Keyword):
    keyword = "pattern"

    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        import re

        self.regex = re.compile(pattern=self.value)

    @correct_type(type_=str)
    def __call__(self, instance):
        if not self.regex.search(instance):
            return ValidationError(messages=[f"{instance} failed {self}"])
        return True
