from jschema.common import KeywordGroup, ValidationResult


class Max(KeywordGroup):
    value: int
    # TODO(ope): should I make this constructor, abstract?

    def validate(self, instance):
        if self.value < len(instance):
            return ValidationResult(ok=False, messages=[])
        return ValidationResult(ok=True)


class Min(KeywordGroup):
    value: int

    def validate(self, instance):
        if len(instance) < self.value:
            return ValidationResult(ok=False, messages=[])
        return ValidationResult(ok=True)


def validate_min(value, instance):
    if len(instance) < value:
        return ValidationResult(ok=False, messages=[])
    return ValidationResult(ok=True)


def validate_max(value, instance):
    if value < len(instance):
        return ValidationResult(ok=False, messages=[])
    return ValidationResult(ok=True)
