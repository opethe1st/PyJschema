from itertools import filterfalse

from pyjschema.common import Keyword, KeywordGroup
from pyjschema.draft_2019_09.context import BUILD_VALIDATOR
from pyjschema.utils import ValidationResult


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

    def __call__(self, instance, location=None):
        if not self._if_validator:
            return True

        res = True
        if self._if_validator(instance=instance, location=location):
            if self._then_validator:
                res = self._then_validator(
                    instance=instance, location=location
                )  # this location is wrong
        else:
            if self._else_validator:
                res = self._else_validator(
                    instance=instance, location=location
                )  # this location is wrong
        return (
            True
            if res
            else ValidationResult(
                message="failed if then else",
                keywordLocation=self.location,
                location=location,
                sub_results=[res],
            )
        )

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

    def __call__(self, instance, location=None):
        results = filterfalse(
            bool,
            (
                validator(instance=instance, location=location)
                for validator in self._validators
            ),
        )  # this location is probably wrong
        results = list(results)
        return (
            True
            if not results
            else ValidationResult(
                message="failed allOf",
                keywordLocation=self.location,
                location=location,
                sub_results=[results],
            )
        )

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

    def __call__(self, instance, location=None):
        results = list(
            filterfalse(
                bool,
                (
                    validator(instance=instance, location=location)
                    for validator in self._validators
                ),  # this location is probably wrong
            )
        )
        return (
            True
            if len(results) == (len(self._validators) - 1)
            else ValidationResult(
                message="failed oneOf",
                keywordLocation=self.location,
                location=location,
                sub_results=results,
            )
        )


class AnyOf(Keyword):
    keyword = "anyOf"

    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        build_validator = BUILD_VALIDATOR.get()

        self._validators = [
            build_validator(schema=item, location=f"{self.location}", parent=self)
            for item in self.value
        ]

    def __call__(self, instance, location=None):
        results = filterfalse(
            bool,
            (
                validator(instance=instance, location=location)
                for validator in self._validators
            ),
        )  # this location is probably wrong
        results = list(results)
        return (
            True
            if len(results) < len(self._validators)
            else ValidationResult(
                message="failed AnyOf",
                keywordLocation=self.location,
                location=location,
                sub_results=results,
            )
        )

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

    def __call__(self, instance, location=None):
        # errors populated but not actual error.
        # unset error?
        result = self._validator(instance=instance, location=location)
        return (
            ValidationResult(
                message="failed Not validation",
                location=location,
                keywordLocation=self.location,
                sub_results=[result],
            )
            if result
            else True
        )

    def sub_validators(self):
        if self._validator:
            yield self._validator
