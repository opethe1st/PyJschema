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
        lambda res: not res, (validator(instance=instance) for validator in validators),
    )


def validate_only(type_):
    "this is makes sure that we only validate instance of the correct type"

    def wrapper(validate):
        def wrapped_function(self, instance):
            if isinstance(instance, type_):
                return validate(self=self, instance=instance)
            else:
                return True

        return wrapped_function

    return wrapper
