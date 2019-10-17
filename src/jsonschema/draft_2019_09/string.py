from jsonschema.common import Keyword, Type, ValidationResult

from .common import Max, Min


class _MaxLength(Max):
    def __init__(self, maxLength):
        self.value = maxLength


class _MinLength(Min):
    def __init__(self, minLength):
        self.value = minLength


class _Pattern(Keyword):
    def __init__(self, pattern):
        import re
        self.regex = re.compile(pattern)

    def validate(self, instance):
        if not self.regex.match(instance):
            return ValidationResult(ok=False, messages=["instance doesn't match the pattern given"])
        return ValidationResult(ok=True)


class String(Type):
    KEYWORDS_TO_VALIDATOR = {
        ('minLength',): _MinLength,
        ('maxLength',): _MaxLength,
        ('pattern',): _Pattern,
    }
    type_ = str
