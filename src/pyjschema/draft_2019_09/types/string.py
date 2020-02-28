from pyjschema.common import Keyword

from .common import validate_max, validate_min, validate_only


class _MaxLength(Keyword):
    keyword = "maxLength"

    @validate_only(type_=str)
    def __call__(self, instance, output, location=None):
        return validate_max(
            value=self.value, instance=instance, output=output, location=location, keyword_location=self.location
        )


class _MinLength(Keyword):
    keyword = "minLength"

    @validate_only(type_=str)
    def __call__(self, instance, output, location=None):
        return validate_min(
            value=self.value, instance=instance, output=output, location=location, keyword_location=self.location
        )


class _Pattern(Keyword):
    keyword = "pattern"

    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        import re

        self.regex = re.compile(pattern=self.value)

    @validate_only(type_=str)
    def __call__(self, instance, output, location=None):
        if not self.regex.search(instance):
            return False
        return True
