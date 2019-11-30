from jschema.common import KeywordGroup, Primitive, ValidationError

from .common import validate_max, validate_min
from .type_base import Type


class _MaxLength(KeywordGroup):
    def __init__(self, maxLength: Primitive):
        self.value = maxLength.value

    def validate(self, instance):
        return validate_max(value=self.value, instance=instance, message=f"{instance} failed {self}")

    def __repr__(self):
        return f"Maximum(value={self.value})"


class _MinLength(KeywordGroup):
    def __init__(self, minLength: Primitive):
        self.value = minLength.value

    def validate(self, instance):
        return validate_min(value=self.value, instance=instance, message=f"{instance} failed {self}")

    def __repr__(self):
        return f"Minimum(value={self.value})"


class _Pattern(KeywordGroup):
    def __init__(self, pattern: Primitive):
        import re
        self.value = pattern
        self.regex = re.compile(pattern=pattern.value)

    def validate(self, instance):
        if not self.regex.search(instance):
            return ValidationError(
                messages=[f"{instance} failed {self}"]
            )
        return True

    def __repr__(self):
        return f"Pattern(value={self.value})"


class String(Type):
    KEYWORDS_TO_VALIDATOR = {
        ("minLength",): _MinLength,
        ("maxLength",): _MaxLength,
        ("pattern",): _Pattern,
    }
    type_ = str
