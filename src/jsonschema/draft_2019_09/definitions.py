from jsonschema.common import Keyword, ValidationResult


class Def(Keyword):

    def __init__(self, definitions):
        from .validator import build_validator

        self._validators = {key: build_validator(value) for key, value in definitions.items()}

    def validate(self, instance):
        return ValidationResult(ok=True)

    def subschema_validators(self):
        return list(self._validators.values())
