import typing as t

from jsonschema.common import Keyword, ValidationResult, Schema


class Defs(Keyword):
    def __init__(self, defs: t.Dict[str, Schema]):
        from .validator import build_validator

        self._validators = {key: build_validator(value) for key, value in defs.items()}

    def validate(self, instance):
        return ValidationResult(ok=True)

    def subschema_validators(self):
        for validator in self._validators.values():
            yield validator
