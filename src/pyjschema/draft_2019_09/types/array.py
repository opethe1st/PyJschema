import typing

from pyjschema.common import Keyword, KeywordGroup
from pyjschema.draft_2019_09.context import BUILD_VALIDATOR
from pyjschema.utils import basic_output, validate_only


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

    @basic_output("this fails for items and additional_item")
    @validate_only(type_=list)
    def __call__(self, instance, location=None):
        if self._items_validator:
            return self._validate_items(instance=instance, location=location)
        elif self._items_validators:
            return self._validate_items_list(instance=instance, location=location)
        return True

    def _validate_items(self, instance, location):
        results = filter(
            lambda res: not res,
            (
                self._items_validator(instance=value, location=f"{location}/{i}")
                for i, value in enumerate(instance)
            ),
        )
        first_result = next(results, True)
        if first_result:
            return True
        else:
            return False

    def _validate_items_list(self, instance, location):
        results = _validate_item_list(
            items_validators=self._items_validators,
            additional_items_validator=self._additional_items_validator,
            instance=instance,
            location=location,
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


def _validate_item_list(
    items_validators, additional_items_validator, instance, location
):

    i = 0
    while i < len(items_validators):
        if i >= len(instance):
            break

        res = items_validators[i](instance[i], location=f"{location}/{i}")

        if not res:
            yield res

        i += 1

    # additionalItem for the rest of the items in the instance
    if additional_items_validator:
        while i < len(instance):
            res = additional_items_validator(instance[i], location=f"{location}/{i}")

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

    @basic_output("this instance: {instance} does not contain ")
    @validate_only(type_=list)
    def __call__(self, instance, location=None):

        if self._validator:
            count = 0
            for value in instance:
                res = self._validator(instance=value, location=location)

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

    @basic_output("This has less than {value} items")
    @validate_only(type_=list)
    def __call__(self, instance, location=None):
        return self.value <= len(instance)


class _MaxItems(Keyword):
    keyword = "maxItems"

    @basic_output("This has more than {value} items")
    @validate_only(type_=list)
    def __call__(self, instance, location=None):
        return len(instance) <= self.value


class _UniqueItems(Keyword):
    keyword = "uniqueItems"

    @basic_output("This doesnt have unique items")
    @validate_only(type_=list)
    def __call__(self, instance, location=None):
        if self.value:
            itemsset = set([str(value) for value in instance])

            # TODO(ope) - actually make sure the values are unique - is this even possible?
            if len(itemsset) != len(instance):
                return False

        return True
