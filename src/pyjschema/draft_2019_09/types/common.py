import typing

from pyjschema.common import AValidator


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
