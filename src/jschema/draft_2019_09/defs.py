from jschema.common import Instance, KeywordGroup, ValidationResult


class Defs(KeywordGroup):
    """
    This is corresponds to the $defs keyword
    """

    def __init__(self, schema: Instance):
        defs = schema.value["$defs"]
        from .validator_construction import build_validator

        self._validators = {
            key: build_validator(schema=value) for key, value in defs.value.items()
        }

    def validate(self, instance):
        return ValidationResult(ok=True)

    def subschema_validators(self):
        for validator in self._validators.values():
            yield validator
