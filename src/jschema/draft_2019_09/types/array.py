import typing as t
import itertools
from jschema.common import Dict, KeywordGroup, List, ValidationError

from .common import validate_max, validate_min
from .type_ import Type


class _Items(KeywordGroup):
    def __init__(self, schema: Dict):
        items = schema.get("items")
        additionalItems = schema.get("additionalItems")
        from jschema.draft_2019_09 import build_validator
        from jschema.draft_2019_09.validator_construction import (
            BuildValidatorResultType,
        )

        self._items_validator: t.Optional[BuildValidatorResultType] = None
        self._items_validators: t.List[BuildValidatorResultType] = []
        self._additional_items_validator: t.Optional[BuildValidatorResultType] = None
        if items:
            if isinstance(items, List):
                self._items_validators = [
                    build_validator(schema=schema) for schema in items
                ]
                if items and additionalItems:
                    self._additional_items_validator = build_validator(
                        schema=additionalItems
                    )
            else:  # add to add this condition
                self._items_validator = build_validator(schema=items)

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


class _Contains(KeywordGroup):
    def __init__(self, schema: Dict):
        from jschema.draft_2019_09 import build_validator

        contains = schema.get("contains")
        maxContains = schema.get("maxContains")
        minContains = schema.get("minContains")

        self._validator = build_validator(schema=contains) if contains else None
        self.maxContainsValue = maxContains.value if maxContains else float("inf")
        self.minContainsValue = minContains.value if minContains else -float("inf")

    def validate(self, instance):

        if self._validator:
            count = 0
            for value in instance:
                # should just be one validator
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


class _MinItems(KeywordGroup):
    def __init__(self, schema: Dict):
        self.value = schema["minItems"].value

    def validate(self, instance):
        return validate_min(value=self.value, instance=instance)


class _MaxItems(KeywordGroup):
    def __init__(self, schema: Dict):
        self.value = schema["maxItems"].value

    def validate(self, instance):
        return validate_max(value=self.value, instance=instance)


class _UniqueItems(KeywordGroup):
    def __init__(self, schema: Dict):
        self.value = schema["uniqueItems"].value

    def validate(self, instance):
        if self.value:
            itemsset = set([str(value) for value in instance])

            if len(itemsset) != len(instance):
                return ValidationError()
            # TODO(ope) - actually make sure the values are unique - is this even possible?

        return True


class Array(Type):

    KEYWORDS_TO_VALIDATOR = {
        ("minItems",): _MinItems,
        ("maxItems",): _MaxItems,
        ("uniqueItems",): _UniqueItems,
        ("contains", "maxContains", "minContains"): _Contains,
        ("items", "additionalItems"): _Items,
    }

    type_ = list
