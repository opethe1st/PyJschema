from pyjschema.common import Dict, KeywordGroup, ValidationError


class If(KeywordGroup):

    def __init__(self, schema: Dict, location=None):
        super().__init__(schema=schema, location=location)
        from .validator_construction import build_validator

        self._if_validator = build_validator(schema=schema["if"], location=f"{location}/if")
        self._then_validator = (
            build_validator(schema=schema["then"], location=f"{location}/then") if schema.get("then") else None
        )
        self._else_validator = (
            build_validator(schema=schema["else"], location=f"{location}/else") if schema.get("else") else None
        )

    def validate(self, instance):
        # import pdb; pdb.set_trace()
        if self._if_validator.validate(instance=instance):
            if self._then_validator:
                return self._then_validator.validate(instance=instance)
        else:
            if self._else_validator:
                return self._else_validator.validate(instance=instance)
        return True

    def sub_validators(self):
        yield self._if_validator
        if self._then_validator:
            yield self._then_validator
        if self._else_validator:
            yield self._else_validator


class AllOf(KeywordGroup):
    def __init__(self, schema: Dict, location=None):
        super().__init__(schema=schema, location=location)
        from .validator_construction import build_validator

        self._validators = [build_validator(schema=item, location=f"{location}/allOf") for item in schema["allOf"]]

    def validate(self, instance):
        ok = all(
            validator.validate(instance=instance) for validator in self._validators
        )
        return True if ok else ValidationError()

    # WOAH: Not defining this resulted in an almost impossible to debug bug. SIGH!
    # How do I prevent that in future
    # this is required if a keyword
    def sub_validators(self):
        yield from self._validators


class OneOf(KeywordGroup):
    def __init__(self, schema: Dict, location=None):
        super().__init__(schema=schema, location=location)
        from .validator_construction import build_validator

        self._validators = [build_validator(schema=item, location=f"{location}/oneOf") for item in schema["oneOf"]]

    def validate(self, instance):
        oks = list(
            filter(
                lambda res: res,
                (
                    validator.validate(instance=instance)
                    for validator in self._validators
                ),
            )
        )
        return True if len(oks) == 1 else ValidationError()


class AnyOf(KeywordGroup):
    def __init__(self, schema: Dict, location=None):
        super().__init__(schema=schema, location=location)
        from .validator_construction import build_validator

        self._validators = [build_validator(schema=item, location=f"{location}/anyOf") for item in schema["anyOf"]]

    def validate(self, instance):
        ok = any(
            validator.validate(instance=instance) for validator in self._validators
        )
        return True if ok else ValidationError()

    # WOAH: Not defining this resulted in an almost impossible to debug bug. SIGH!
    # How do I prevent that in future
    def sub_validators(self):
        yield from self._validators


class Not(KeywordGroup):
    def __init__(self, schema: Dict, location=None):
        super().__init__(schema=schema, location=location)
        from .validator_construction import build_validator

        self._validator = build_validator(schema=schema["not"], location=f"{location}/not")

    def validate(self, instance):
        result = self._validator.validate(instance=instance)
        return ValidationError(messages=["not"]) if result else True

    # WOAH: Not defining this resulted in an almost impossible to debug bug. SIGH!
    # How do I prevent that in future
    def sub_validators(self):
        if self._validator:
            yield self._validator
