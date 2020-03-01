from pyjschema.common import Keyword
from pyjschema.utils import basic_output, validate_only


class _MaxLength(Keyword):
    keyword = "maxLength"

    @basic_output("{instance!r}'s length is more than max_length: {value!r}")
    @validate_only(type_=str)
    def __call__(self, instance, location=None):
        return len(instance) <= self.value


class _MinLength(Keyword):
    keyword = "minLength"

    @basic_output("{instance!r}'s length is less than min_length: {value!r}")
    @validate_only(type_=str)
    def __call__(self, instance, location=None):
        return self.value <= len(instance)


class _Pattern(Keyword):
    keyword = "pattern"

    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        import re

        self.regex = re.compile(pattern=self.value)

    @basic_output("{instance!r} doesnt match this pattern: {value!r}")
    @validate_only(type_=str)
    def __call__(self, instance, location=None):
        if not self.regex.search(instance):
            return False
        return True
