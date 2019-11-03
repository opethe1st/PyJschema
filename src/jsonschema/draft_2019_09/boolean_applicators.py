
from jsonschema.common import (
    Instance,
    KeywordGroup,
    ValidationResult,
)


class If(KeywordGroup):
    def __init__(self, schema: Instance):
        from .validator import build_validator

        self._if_validator = build_validator(schema=schema.value["if"])
        self._then_validator = (
            build_validator(schema=schema.value["then"])
            if schema.value.get("then")
            else None
        )
        self._else_validator = (
            build_validator(schema=schema.value["else"])
            if schema.value.get("else")
            else None
        )

    def validate(self, instance):
        if self._if_validator.validate(instance=instance).ok:
            if self._then_validator:
                return self._then_validator.validate(instance=instance)
        else:
            if self._else_validator:
                return self._else_validator.validate(instance=instance)
        return ValidationResult(ok=True)

    def subschema_validators(self):
        yield self._if_validator
        if self._then_validator:
            yield self._then_validator
        if self._else_validator:
            yield self._else_validator
