import typing as t

from jsonschema.common import Keyword, Schema, ValidationResult

from .annotate import Instance


class Defs(Keyword):
    def __init__(self, defs: Instance):
        from .validator import build_validator

        self._validators = {key: build_validator(schema=value) for key, value in defs.value.items()}

    def validate(self, instance):
        return ValidationResult(ok=True)

    def subschema_validators(self):
        for validator in self._validators.values():
            yield validator
