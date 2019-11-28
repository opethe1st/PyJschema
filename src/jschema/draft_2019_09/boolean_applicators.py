from jschema.common import Dict, KeywordGroup, ValidationResult


class If(KeywordGroup):

    # TODO(ope): this accepts a schema, probably should accept if, then, else
    # but that wont work since they are reserved keywords. Maybe the decision to pass in individual keywords was
    # misguided but I also wanted to document that a particular keyword group deals with these keywords
    def __init__(self, schema: Dict):
        from .validator_construction import build_validator

        self._if_validator = build_validator(schema=schema["if"])
        self._then_validator = (
            build_validator(schema=schema["then"])
            if schema.get("then")
            else None
        )
        self._else_validator = (
            build_validator(schema=schema["else"])
            if schema.get("else")
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


class AllOf(KeywordGroup):
    def __init__(self, schema: Dict):
        from .validator_construction import build_validator

        self._validators = [
            build_validator(schema=item) for item in schema["allOf"]
        ]

    def validate(self, instance):
        ok = all(
            validator.validate(instance=instance).ok for validator in self._validators
        )
        return ValidationResult(ok=ok)

    # WOAH: Not defining this resulted in an almost impossible to debug bug. SIGH!
    # How do I prevent that in future
    # this is required if a keyword
    def subschema_validators(self):
        yield from self._validators


class OneOf(KeywordGroup):
    def __init__(self, schema: Dict):
        from .validator_construction import build_validator

        self._validators = [
            build_validator(schema=item) for item in schema["oneOf"]
        ]

    def validate(self, instance):
        oks = list(
            filter(
                lambda res: res.ok,
                (
                    validator.validate(instance=instance)
                    for validator in self._validators
                ),
            )
        )
        ok = len(oks) == 1
        return ValidationResult(ok=ok)

    # WOAH: Not defining this resulted in an almost impossible to debug bug. SIGH!
    # How do I prevent that in future
    def subschema_validators(self):
        yield from self._validators


class AnyOf(KeywordGroup):
    def __init__(self, schema: Dict):
        from .validator_construction import build_validator

        self._validators = [
            build_validator(schema=item) for item in schema["anyOf"]
        ]

    def validate(self, instance):
        ok = any(
            validator.validate(instance=instance).ok for validator in self._validators
        )
        return ValidationResult(ok=ok)

    # WOAH: Not defining this resulted in an almost impossible to debug bug. SIGH!
    # How do I prevent that in future
    def subschema_validators(self):
        yield from self._validators


class Not(KeywordGroup):
    def __init__(self, schema: Dict):
        from .validator_construction import build_validator

        self._validator = build_validator(schema=schema["not"])

    def validate(self, instance):
        ok = not self._validator.validate(instance=instance).ok
        return ValidationResult(ok=ok)

    # WOAH: Not defining this resulted in an almost impossible to debug bug. SIGH!
    # How do I prevent that in future
    def subschema_validators(self):
        if self._validator:
            yield self._validator
