from pyjschema.common import KeywordGroup, ValidationError, Keyword


class If(KeywordGroup):

    def __init__(self, schema: dict, location=None, parent=None):
        from .validator_construction import build_validator

        self._if_validator = build_validator(schema=schema["if"], location=f"{location}/if", parent=self)
        self._then_validator = (
            build_validator(schema=schema["then"], location=f"{location}/then", parent=self) if schema.get("then") else None
        )
        self._else_validator = (
            build_validator(schema=schema["else"], location=f"{location}/else", parent=self) if schema.get("else") else None
        )

    def validate(self, instance):
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


class AllOf(Keyword):
    keyword = "allOf"

    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        from .validator_construction import build_validator

        self._validators = [build_validator(schema=item, location=f"{self.location}", parent=self) for item in self.value]

    def validate(self, instance):
        ok = all(
            validator.validate(instance=instance) for validator in self._validators
        )
        return True if ok else ValidationError()

    def sub_validators(self):
        yield from self._validators


class OneOf(Keyword):
    keyword = "oneOf"

    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        from .validator_construction import build_validator

        self._validators = [build_validator(schema=item, location=self.location, parent=self) for item in self.value]

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


class AnyOf(Keyword):
    keyword = "anyOf"

    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        from .validator_construction import build_validator

        self._validators = [build_validator(schema=item, location=f"{self.location}", parent=self) for item in self.value]

    def validate(self, instance):
        ok = any(
            validator.validate(instance=instance) for validator in self._validators
        )
        return True if ok else ValidationError()

    def sub_validators(self):
        yield from self._validators


class Not(Keyword):
    keyword = "not"

    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        from .validator_construction import build_validator

        self._validator = build_validator(schema=self.value, location=f"{self.location}", parent=self)

    def validate(self, instance):
        result = self._validator.validate(instance=instance)
        return ValidationError(messages=["not {self._validator}"]) if result else True

    def sub_validators(self):
        if self._validator:
            yield self._validator
