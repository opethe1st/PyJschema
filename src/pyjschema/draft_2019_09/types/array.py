import itertools
import typing

from pyjschema.common import Keyword, KeywordGroup, ValidationError

from .common import correct_type, validate_max, validate_min


class _Items(KeywordGroup):
    def __init__(self, schema: dict, location=None, parent=None):
        from pyjschema.draft_2019_09 import build_validator
        from pyjschema.draft_2019_09.validator_construction import (
            BuildValidatorResultType,
        )

        self.parent = parent

        items = schema.get("items")
        additionalItems = schema.get("additionalItems")

        self._items_validator: typing.Optional[BuildValidatorResultType] = None
        self._items_validators: typing.List[BuildValidatorResultType] = []
        self._additional_items_validator: typing.Optional[
            BuildValidatorResultType
        ] = None
        if items is not None:
            if isinstance(items, list):
                self._items_validators = [
                    build_validator(
                        schema=schema, location=f"{location}/items/{i}", parent=self
                    )
                    for i, schema in enumerate(items)
                ]
                if items is not None and additionalItems is not None:
                    self._additional_items_validator = build_validator(
                        schema=additionalItems,
                        location=f"{location}/additionalItems",
                        parent=self,
                    )
            else:
                self._items_validator = build_validator(
                    schema=items, location=f"{location}/items", parent=self
                )

    def __repr__(self):
        return f"Items(items_validator(s)={self._items_validator or self._items_validators}, add_item_validator={self._additional_items_validator})"

    @correct_type(type_=list)
    def validate(self, instance):
        if self._items_validator:
            return self._validate_items(instance=instance)
        elif self._items_validators:
            return self._validate_items_list(instance=instance)
        return True

    def _validate_items(self, instance):
        # TODO: shouldnt call this errors, more like results
        errors = filter(
            lambda res: not res,
            (self._items_validator.validate(value) for value in instance),
        )
        first_result = next(errors, True)
        if first_result:
            return True
        else:
            return ValidationError(children=itertools.chain([first_result], errors))

    def _validate_items_list(self, instance):
        results = _validate_item_list(
            items_validators=self._items_validators,
            additional_items_validator=self._additional_items_validator,
            instance=instance,
        )
        first_res = next(results, True)

        if first_res:
            return True
        else:
            return ValidationError(children=itertools.chain([first_res], results))

    def sub_validators(self):
        if self._items_validator:
            yield self._items_validator
        for validator in self._items_validators:
            yield validator
        if self._additional_items_validator:
            yield self._additional_items_validator


def _validate_item_list(items_validators, additional_items_validator, instance):
    if isinstance(instance, list):

        i = 0
        while i < len(items_validators):
            if i >= len(instance):
                break

            res = items_validators[i].validate(instance[i])

            if not res:
                yield res

            i += 1

        # additionalItem for the rest of the items in the instance
        if additional_items_validator:
            while i < len(instance):
                res = additional_items_validator.validate(instance[i])

                if not res:
                    yield res

                i += 1
    else:
        yield ValidationError()


class _Contains(KeywordGroup):
    def __init__(self, schema: dict, location=None, parent=None):
        from pyjschema.draft_2019_09 import build_validator

        contains = schema.get("contains")
        maxContains = schema.get("maxContains")
        minContains = schema.get("minContains")

        self._validator = (
            build_validator(
                schema=contains, location=f"{location}/contains", parent=self
            )
            if contains is not None
            else None
        )
        self.maxContainsValue = maxContains if maxContains else float("inf")
        self.minContainsValue = minContains if minContains else -float("inf")

    @correct_type(type_=list)
    def validate(self, instance):

        if self._validator:
            count = 0
            for value in instance:
                res = self._validator.validate(value)

                if res:
                    count += 1

            if count and (self.minContainsValue <= count <= self.maxContainsValue):
                return True

            if not (self.minContainsValue <= count <= self.maxContainsValue):
                return ValidationError(
                    messages=[
                        f"The number of items matching the contains keyword is not less than or equal to {self.minContainsValue} or greater than or equal to {self.maxContainsValue}"
                    ]
                )

            return ValidationError(
                messages=[
                    "No item in this array matches the schema in the contains keyword"
                ]
            )
        else:
            return True

    def sub_validators(self):
        if self._validator:
            yield self._validator


class _MinItems(Keyword):
    keyword = "minItems"

    @correct_type(type_=list)
    def validate(self, instance):
        return validate_min(value=self.value, instance=instance)


class _MaxItems(Keyword):
    keyword = "maxItems"

    @correct_type(type_=list)
    def validate(self, instance):
        return validate_max(value=self.value, instance=instance)


class _UniqueItems(Keyword):
    keyword = "uniqueItems"

    @correct_type(type_=list)
    def validate(self, instance):
        if self.value:
            itemsset = set([str(value) for value in instance])

            if len(itemsset) != len(instance):
                return ValidationError()
            # TODO(ope) - actually make sure the values are unique - is this even possible?

        return True
