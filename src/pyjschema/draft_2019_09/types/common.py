import typing

from pyjschema.common import AValidator


def validate_min(value, instance):
    if len(instance) < value:
        return False
    return True


def validate_max(value, instance):
    if value < len(instance):
        return False
    return True


def validate_instance_against_all_validators(
    validators: typing.Dict[str, AValidator], instance, location
):
    yield from filter(
        lambda res: not res,
        (
            validator(instance=instance, location=f"{location}/{key}")
            for key, validator in validators.items()
        ),
    )
