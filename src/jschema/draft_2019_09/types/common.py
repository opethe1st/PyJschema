import typing

from jschema.common import AValidator, ValidationError


def validate_min(value, instance):
    if len(instance) < value:
        return ValidationError(messages=[])
    return True


def validate_max(value, instance):
    if value < len(instance):
        return ValidationError(messages=[])
    return True


def validate_instance_against_all_validators(
    validators: typing.List[AValidator], instance
):
    yield from filter(
        lambda res: not res,
        (validator.validate(instance=instance) for validator in validators),
    )


def validate_instance_against_any_validator(
    validators: typing.List[AValidator], instance
):
    errors = []

    for validator in validators:
        res = validator.validate(instance=instance)
        if res:
            return
        else:
            errors.append(res)

    yield from errors
