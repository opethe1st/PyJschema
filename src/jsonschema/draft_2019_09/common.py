import typing as t

from jsonschema.common import Keyword, ValidationResult


class Max(Keyword):
    value: int
    # TODO(ope): should I make this constructor, abstract?

    def validate(self, instance):
        if self.value < len(instance):
            return ValidationResult(ok=False, messages=[])
        return ValidationResult(ok=True)


class Min(Keyword):
    value: int

    def validate(self, instance):
        if len(instance) < self.value:
            return ValidationResult(ok=False, messages=[])
        return ValidationResult(ok=True)
