import typing

from pyjschema.common import AValidator, ValidationError


def validate_min(value, instance, message=""):
    if len(instance) < value:
        return ValidationError(messages=[message])
    return True


def validate_max(value, instance, message=""):
    if value < len(instance):
        return ValidationError(messages=[message])
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
            return True
        else:
            errors.append(res)

    yield from errors


def correct_type(type_):
    def wrapper(func):
        def wrapped_function(self, instance):
            if isinstance(instance, type_):
                return func(self=self, instance=instance)
            else:
                return True

        return wrapped_function

    return wrapper
