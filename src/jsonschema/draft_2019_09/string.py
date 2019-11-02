import typing as t

from jsonschema.common import Keyword, Type, ValidationResult

from .common import Max, Min
from .annotate import Instance

class _MaxLength(Max):
    def __init__(self, maxLength: Instance):
        self.value = maxLength.value


class _MinLength(Min):
    def __init__(self, minLength: Instance):
        self.value = minLength.value


class _Pattern(Keyword):
    def __init__(self, pattern: Instance):
        import re

        self.regex = re.compile(pattern.value)

    def validate(self, instance):
        if not self.regex.match(instance):
            return ValidationResult(
                ok=False, messages=["instance doesn't match the pattern given"]
            )
        return ValidationResult(ok=True)


class String(Type):
    KEYWORDS_TO_VALIDATOR = {
        ("minLength",): _MinLength,
        ("maxLength",): _MaxLength,
        ("pattern",): _Pattern,
    }
    type_ = str
