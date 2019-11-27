from jschema.common import Instance, KeywordGroup, Type, ValidationResult
from .common import validate_max, validate_min


class _MaxLength(KeywordGroup):
    def __init__(self, maxLength: Instance):
        self.value = maxLength.value

    def validate(self, instance):
        return validate_max(value=self.value, instance=instance)


class _MinLength(KeywordGroup):
    def __init__(self, minLength: Instance):
        self.value = minLength.value

    def validate(self, instance):
        return validate_min(value=self.value, instance=instance)


class _Pattern(KeywordGroup):
    def __init__(self, pattern: Instance):
        import re
        self.regex = re.compile(pattern=pattern.value)

    def validate(self, instance):
        if not self.regex.search(instance):
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
