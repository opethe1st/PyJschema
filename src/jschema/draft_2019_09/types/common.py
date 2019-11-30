from jschema.common import ValidationError


def validate_min(value, instance):
    if len(instance) < value:
        return ValidationError(messages=[])
    return True


def validate_max(value, instance):
    if value < len(instance):
        return ValidationError(messages=[])
    return True
