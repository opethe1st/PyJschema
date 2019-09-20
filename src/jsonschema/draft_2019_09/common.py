from jsonschema.common import Keyword, ValidationResult


class Max(Keyword):
    def __init__(self, value: int):
        self.value = value

    def validate(self, instance):
        if self.value < len(instance):
            return ValidationResult(ok=False, messages=[])
        return ValidationResult(ok=True)


class Min(Keyword):
    def __init__(self, value: int):
        self.value = value

    def validate(self, instance):
        if len(instance) < self.value:
            return ValidationResult(ok=False, messages=[])
        return ValidationResult(ok=True)
