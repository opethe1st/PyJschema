from jschema.common import Instance, Keyword, Type, ValidationResult
from jschema.common.utils import re_compile
from .common import Max, Min


class _MaxLength(Max):
    def __init__(self, maxLength: Instance):
        self.value = maxLength.value


class _MinLength(Min):
    def __init__(self, minLength: Instance):
        self.value = minLength.value


class _Pattern(Keyword):
    def __init__(self, pattern: Instance):
        self.regex = re_compile(pattern=pattern.value)

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
