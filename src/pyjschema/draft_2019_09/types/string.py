from pyjschema.common import Dict, KeywordGroup, ValidationError

from .common import validate_max, validate_min
from .type_ import Type


class _MaxLength(KeywordGroup):
    def __init__(self, schema: Dict):
        super().__init__(schema=schema)
        self.value = schema["maxLength"]

    def validate(self, instance):
        return validate_max(
            value=self.value, instance=instance, message=f"{instance} failed {self}"
        )

    def __repr__(self):
        return f"Maximum(value={self.value})"


class _MinLength(KeywordGroup):
    def __init__(self, schema: Dict):
        super().__init__(schema=schema)
        self.value = schema["minLength"]

    def validate(self, instance):
        return validate_min(
            value=self.value, instance=instance, message=f"{instance} failed {self}"
        )

    def __repr__(self):
        return f"Minimum(value={self.value})"


class _Pattern(KeywordGroup):
    def __init__(self, schema: Dict):
        super().__init__(schema=schema)
        import re

        self.value = schema["pattern"]
        self.regex = re.compile(pattern=self.value)

    def validate(self, instance):
        if not self.regex.search(instance):
            return ValidationError(messages=[f"{instance} failed {self}"])
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
