from pyjschema.common import Keyword, KeywordGroup
from pyjschema.draft_2019_09.context import BUILD_VALIDATOR
from pyjschema.utils import basic_output


class IfElseThen(KeywordGroup):
    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        build_validator = BUILD_VALIDATOR.get()

        self._if_validator = (
            build_validator(schema=schema["if"], location=f"{location}/if", parent=self)
            if schema.get("if")
            else None
        )
        self._then_validator = (
            build_validator(
                schema=schema["then"], location=f"{location}/then", parent=self
            )
            if schema.get("then") and schema.get("if")
            else None
        )
        self._else_validator = (
            build_validator(
                schema=schema["else"], location=f"{location}/else", parent=self
            )
            if schema.get("else") and schema.get("if")
            else None
        )

    @basic_output("failed if then else")
    def __call__(self, instance, output, location=None):
        if not self._if_validator:
            return True
        if self._if_validator(instance=instance, output=output, location=location):
            if self._then_validator:
                return self._then_validator(instance=instance, output=output, location=location) # this location is wrong
        else:
            if self._else_validator:
                return self._else_validator(instance=instance, output=output, location=location)  # this location is wrong
        return True

    def sub_validators(self):
        if self._if_validator:
            yield self._if_validator
        if self._then_validator:
            yield self._then_validator
        if self._else_validator:
            yield self._else_validator


class AllOf(Keyword):
    keyword = "allOf"

    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        build_validator = BUILD_VALIDATOR.get()

        self._validators = [
            build_validator(schema=item, location=f"{self.location}", parent=self)
            for item in self.value
        ]

    @basic_output("fail allOf")
    def __call__(self, instance, output, location=None):
        ok = all(validator(instance=instance, output=output, location=location) for validator in self._validators)  # this location is probably wrong
        return True if ok else False

    def sub_validators(self):
        yield from self._validators


class OneOf(Keyword):
    keyword = "oneOf"

    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        build_validator = BUILD_VALIDATOR.get()

        self._validators = [
            build_validator(schema=item, location=self.location, parent=self)
            for item in self.value
        ]

    @basic_output("fail OneOf")
    def __call__(self, instance, output, location=None):
        oks = list(
            filter(
                lambda res: res,
                (validator(instance=instance, output=output, location=location) for validator in self._validators), # this location is probably wrong
            )
        )
        return True if len(oks) == 1 else False


class AnyOf(Keyword):
    keyword = "anyOf"

    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        build_validator = BUILD_VALIDATOR.get()

        self._validators = [
            build_validator(schema=item, location=f"{self.location}", parent=self)
            for item in self.value
        ]

    @basic_output("fail AnyOf")
    def __call__(self, instance, output, location=None):
        ok = any(validator(instance=instance, output=output, location=location) for validator in self._validators)  # this location is probably wrong
        return True if ok else False

    def sub_validators(self):
        yield from self._validators


class Not(Keyword):
    keyword = "not"

    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        build_validator = BUILD_VALIDATOR.get()

        self._validator = build_validator(
            schema=self.value, location=f"{self.location}", parent=self
        )

    @basic_output("failed Not validation")
    def __call__(self, instance, output, location=None):
        result = self._validator(instance=instance, output=output, location=location)
        return False if result else True

    def sub_validators(self):
        if self._validator:
            yield self._validator
