from jsonschema.common import Keyword, Type, ValidationResult
import typing as t
from .common import Max, Min


class _MaxLength(Max):
    def __init__(self, maxLength: int):
        self.value = maxLength


class _MinLength(Min):
    def __init__(self, minLength: int):
        self.value = minLength


class _Pattern(Keyword):
    def __init__(self, pattern: t.Pattern):
        import re

        self.regex = re.compile(pattern)

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
