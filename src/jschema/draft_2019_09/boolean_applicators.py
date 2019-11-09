
from jschema.common import (
    Instance,
    Keyword,
    KeywordGroup,
    ValidationResult,
)


class If(KeywordGroup):

    # TODO(ope): this accepts a schema, probably should accept if, then, else
    # but that wont work since they are reserved keywords. Maybe the decision to pass in individual keywords was
    # misguided but I also wanted to document that a particular keyword group deals with these keywords
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


class AllOf(Keyword):

    def __init__(self, schema: Instance):
        from .validator import build_validator

        self._validators = [build_validator(schema=item) for item in schema.value["allOf"].value]

    def validate(self, instance):
        ok = all(
            validator.validate(instance=instance).ok for validator in self._validators
        )
        return ValidationResult(ok=ok)

    # WOAH: Not defining this resulted in an almost impossible to debug bug. SIGH!
    # How do I prevent that in future
    # this is required if a keyword
    def subschema_validators(self):
        for validator in self._validators:
            yield validator


class OneOf(Keyword):

    def __init__(self, schema: Instance):
        from .validator import build_validator

        self._validators = [build_validator(schema=item) for item in schema.value["oneOf"].value]

    def validate(self, instance):
        oks = list(filter(
            lambda res: res.ok,
            (validator.validate(instance=instance) for validator in self._validators)
        ))
        ok = (len(oks) == 1)
        return ValidationResult(ok=ok)

    # WOAH: Not defining this resulted in an almost impossible to debug bug. SIGH!
    # How do I prevent that in future
    def subschema_validators(self):
        for validator in self._validators:
            yield validator


class AnyOf(Keyword):

    def __init__(self, schema: Instance):
        from .validator import build_validator

        self._validators = [build_validator(schema=item) for item in schema.value["anyOf"].value]

    def validate(self, instance):
        ok = any(
            validator.validate(instance=instance).ok for validator in self._validators
        )
        return ValidationResult(ok=ok)

    # WOAH: Not defining this resulted in an almost impossible to debug bug. SIGH!
    # How do I prevent that in future
    def subschema_validators(self):
        for validator in self._validators:
            yield validator


class Not(Keyword):

    def __init__(self, schema: Instance):
        from .validator import build_validator

        self._validator = build_validator(schema=schema.value["not"])

    def validate(self, instance):
        ok = not self._validator.validate(instance=instance).ok
        return ValidationResult(ok=ok)

    # WOAH: Not defining this resulted in an almost impossible to debug bug. SIGH!
    # How do I prevent that in future
    def subschema_validators(self):
        if self._validator:
            yield self._validator
