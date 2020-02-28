import typing

from pyjschema.common import Keyword, KeywordGroup
from pyjschema.draft_2019_09.context import BUILD_VALIDATOR

from .common import validate_max, validate_min, validate_only


class _Items(KeywordGroup):
    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        build_validator = BUILD_VALIDATOR.get()
        from pyjschema.draft_2019_09.validator_construction import (
            BuildValidatorResultType,
        )

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

    @validate_only(type_=list)
    def __call__(self, instance, output, location=None):
        if self._items_validator:
            return self._validate_items(instance=instance)
        elif self._items_validators:
            return self._validate_items_list(instance=instance)
        return True

    def _validate_items(self, instance):
        # TODO: shouldnt call this errors, more like results
        errors = filter(
            lambda res: not res, (self._items_validator(value) for value in instance),
        )
        first_result = next(errors, True)
        if first_result:
            return True
        else:
            return False

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
            return False

    def sub_validators(self):
        if self._items_validator:
            yield self._items_validator
        for validator in self._items_validators:
            yield validator
        if self._additional_items_validator:
            yield self._additional_items_validator


def _validate_item_list(items_validators, additional_items_validator, instance):

    i = 0
    while i < len(items_validators):
        if i >= len(instance):
            break

        res = items_validators[i](instance[i])

        if not res:
            yield res

        i += 1

    # additionalItem for the rest of the items in the instance
    if additional_items_validator:
        while i < len(instance):
            res = additional_items_validator(instance[i])

            if not res:
                yield res

            i += 1


class _Contains(KeywordGroup):
    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        build_validator = BUILD_VALIDATOR.get()

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

    @validate_only(type_=list)
    def __call__(self, instance, output, location=None):

        if self._validator:
            count = 0
            for value in instance:
                # should just be one validator
                res = self._validator(value)

                if res:
                    count += 1

            if count and (self.minContainsValue <= count <= self.maxContainsValue):
                return True
            return False
        else:
            return True

    def sub_validators(self):
        if self._validator:
            yield self._validator


class _MinItems(Keyword):
    keyword = "minItems"

    @validate_only(type_=list)
    def __call__(self, instance, output, location=None):
        return validate_min(value=self.value, instance=instance)


class _MaxItems(Keyword):
    keyword = "maxItems"

    @validate_only(type_=list)
    def __call__(self, instance, output, location=None):
        return validate_max(value=self.value, instance=instance)


class _UniqueItems(Keyword):
    keyword = "uniqueItems"

    @validate_only(type_=list)
    def __call__(self, instance, output, location=None):
        if self.value:
            itemsset = set([str(value) for value in instance])

            if len(itemsset) != len(instance):
                return False
            # TODO(ope) - actually make sure the values are unique - is this even possible?

        return True
