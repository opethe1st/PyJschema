from pyjschema.common import KeywordGroup, ValidationError

from .common import validate_max, validate_min, correct_type


class _MaxLength(KeywordGroup):
    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        self.value = schema["maxLength"]

    @correct_type(type_=str)
    def validate(self, instance):
        return validate_max(
            value=self.value, instance=instance, message=f"{instance} failed {self}"
        )

    def __repr__(self):
        return f"MaxLength(value={self.value})"


class _MinLength(KeywordGroup):
    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        self.value = schema["minLength"]

    @correct_type(type_=str)
    def validate(self, instance):
        return validate_min(
            value=self.value, instance=instance, message=f"{instance} failed {self}"
        )

    def __repr__(self):
        return f"Minimum(value={self.value})"


class _Pattern(KeywordGroup):
    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        import re

        self.value = schema["pattern"]
        self.regex = re.compile(pattern=self.value)

    @correct_type(type_=str)
    def validate(self, instance):
        if not self.regex.search(instance):
            return ValidationError(messages=[f"{instance} failed {self}"])
        return True

    def __repr__(self):
        return f"Pattern(value={self.value})"
