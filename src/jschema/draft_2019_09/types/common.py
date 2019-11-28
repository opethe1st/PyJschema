from jschema.common import ValidationResult


def validate_min(value, instance):
    if len(instance) < value:
        raise Exception
        return ValidationResult(ok=False, messages=[])
    return ValidationResult(ok=True)


def validate_max(value, instance):
    if value < len(instance):
        raise Exception
        return ValidationResult(ok=False, messages=[])
    return ValidationResult(ok=True)
