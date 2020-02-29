from pyjschema.common import Keyword
from pyjschema.utils import basic_output, validate_only

from .common import validate_max, validate_min


class _MaxLength(Keyword):
    keyword = "maxLength"

    @basic_output("this instance: {instance} length is more than max_length: {value}")
    @validate_only(type_=str)
    def __call__(self, instance, output, location=None):
        return validate_max(
            value=self.value, instance=instance
        )


class _MinLength(Keyword):
    keyword = "minLength"

    @basic_output("this instance: {instance} length is less than min_length: {value}")
    @validate_only(type_=str)
    def __call__(self, instance, output, location=None):
        return validate_min(
            value=self.value, instance=instance
        )


class _Pattern(Keyword):
    keyword = "pattern"

    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        import re

        self.regex = re.compile(pattern=self.value)

    @basic_output("this instance: {instance} doesnt match this pattern: {value}")
    @validate_only(type_=str)
    def __call__(self, instance, output, location=None):
        if not self.regex.search(instance):
            return False
        return True
