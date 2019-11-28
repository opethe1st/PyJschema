from jschema.common import ValidationResult


def validate_min(value, instance):
    if len(instance) < value:
        return ValidationResult(ok=False, messages=[])
    return ValidationResult(ok=True)


def validate_max(value, instance):
    if value < len(instance):
        return ValidationResult(ok=False, messages=[])
    return ValidationResult(ok=True)
