from jsonschema.common import ValidationResult

from .i_validator import IValidator


class Max(IValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if self.value < len(instance):
            return ValidationResult(ok=False, messages=[])
        return ValidationResult(ok=True)


class Min(IValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if len(instance) < self.value:
            return ValidationResult(ok=False, messages=[])
        return ValidationResult(ok=True)
