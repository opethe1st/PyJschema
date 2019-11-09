import typing as t

from jschema.common import (
    Instance,
    Keyword,
    KeywordGroup,
    Type,
    ValidationResult,
)

from .common import Max, Min


class _Items(KeywordGroup):
    def __init__(self, items: Instance, additionalItems: t.Optional[Instance] = None):
        from jschema.draft_2019_09 import build_validator
        from jschema.draft_2019_09.validator_construction import BuildValidatorResultType

        self._items_validator: t.Optional[BuildValidatorResultType] = None
        self._items_validators: t.List[BuildValidatorResultType] = []
        self._additional_items_validator: t.Optional[BuildValidatorResultType] = None
        if items and isinstance(items.value, list):
            self._items_validators = [
                build_validator(schema=schema) for schema in items.value
            ]
            if items and additionalItems:
                self._additional_items_validator = build_validator(
                    schema=additionalItems
                )
        elif items:
            self._items_validator = build_validator(schema=items)

    def validate(self, instance):
        if self._items_validator:
            return self._validate_items(instance=instance)
        elif self._items_validators:
            return self._validate_items_list(instance=instance)
        return ValidationResult(ok=True)

    def _validate_items(self, instance):
        children = []

        for value in instance:
            res = self._items_validator.validate(value)

            if not res.ok:
                children.append(res)

        if not children:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(ok=False, children=children)

    def _validate_items_list(self, instance):
        children = []

        i = 0
        while i < len(self._items_validators):
            if i >= len(instance):
                break

            res = self._items_validators[i].validate(instance[i])

            if not res.ok:
                children.append(res)

            i += 1

        # additionalItem for the rest of the items in the instance
        if self._additional_items_validator:
            while i < len(instance):
                res = self._additional_items_validator.validate(instance[i])

                if not res.ok:
                    children.append(res)

                i += 1

        if children:
            return ValidationResult(ok=False, children=children)
        else:
            return ValidationResult(ok=True)

    def subschema_validators(self):
        if self._items_validator:
            yield self._items_validator
        for validator in self._items_validators:
            yield validator
        if self._additional_items_validator:
            yield self._additional_items_validator


class _Contains(Keyword):
    def __init__(
        self, contains: Instance, maxContains: Instance, minContains: Instance
    ):
        from jschema.draft_2019_09 import build_validator

        self._contains_present = False if contains is None else True
        self._validator = None
        if contains:
            self._validator = build_validator(schema=contains)
        self.maxContainsValue = maxContains.value if maxContains else float("inf")
        self.minContainsValue = minContains.value if minContains else -float("inf")

    def validate(self, instance):

        if self._contains_present:
            contains = False
            count = 0
            for value in instance:
                res = self._validator.validate(value)

                if res.ok:
                    count += 1

                    if not contains:
                        contains = True

            if contains and (self.minContainsValue <= count <= self.maxContainsValue):
                return ValidationResult(ok=True)

            if not (self.minContainsValue <= count <= self.maxContainsValue):
                return ValidationResult(
                    ok=False,
                    messages=[
                        f"The number of items matching the contains keyword is not less than or equal to {self.minContainsValue} or greater than or equal to {self.maxContainsValue}"
                    ],
                )

            return ValidationResult(
                ok=False,
                messages=[
                    "No item in this array matches the schema in the contains keyword"
                ],
            )
        else:
            return ValidationResult(ok=True)

    def subschema_validators(self):
        if self._validator:
            yield self._validator


class _MinItems(Min):
    def __init__(self, minItems: Instance):
        self.value = minItems.value


class _MaxItems(Max):
    def __init__(self, maxItems: Instance):
        self.value = maxItems.value


class _UniqueItems(Keyword):
    def __init__(self, uniqueItems: Instance):
        self.value = uniqueItems.value

    def validate(self, instance):
        if self.value:
            itemsset = set([str(value) for value in instance])

            if len(itemsset) != len(instance):
                return ValidationResult(ok=False)
            # TODO(ope) - actually make sure the values are unique

        return ValidationResult(ok=True)


class Array(Type):

    KEYWORDS_TO_VALIDATOR = {
        ("minItems",): _MinItems,
        ("maxItems",): _MaxItems,
        ("uniqueItems",): _UniqueItems,
        ("contains", "maxContains", "minContains"): _Contains,
        ("items", "additionalItems"): _Items,
    }

    type_ = list
