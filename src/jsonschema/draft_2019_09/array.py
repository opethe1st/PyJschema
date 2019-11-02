import typing as t

from jsonschema.common import (
    AValidator,
    Keyword,
    KeywordGroup,
    Type,
    ValidationResult,
)

from .annotate import Instance
from .common import Max, Min


class _Items(KeywordGroup):
    def __init__(
        self,
        items: Instance,
        additionalItems: t.Optional[Instance] = None,
    ):
        from .validator import build_validator, BuildValidatorResultType

        self._items_validator: t.Optional[BuildValidatorResultType] = None
        self._items_validators: t.List[BuildValidatorResultType] = []
        self._additional_items_validator: t.Optional[BuildValidatorResultType] = None
        if isinstance(items.value, list):
            self._items_validators = [build_validator(schema=schema) for schema in items.value]
            if additionalItems:
                self._additional_items_validator = build_validator(schema=additionalItems)
        else:
            self._items_validator = build_validator(schema=items)

    def validate(self, instance):
        if self._items_validator:
            return self._validate_items(instance=instance)
        elif self._items_validators:
            return self._validate_items_list(instance=instance)
        return ValidationResult(ok=False)

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
    def __init__(self, contains: Instance):
        from .validator import build_validator

        self.location = contains.location
        self._validator = build_validator(schema=contains)

    def validate(self, instance):

        for value in instance:
            res = self._validator.validate(value)

            if res.ok:
                return ValidationResult(ok=True)

        return ValidationResult(
            ok=False,
            messages=[
                "No item in this array matches the schema in the contains keyword"
            ],
        )

    def subschema_validators(self):
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
        ("contains",): _Contains,
        ("items", "additionalItems"): _Items,
    }

    type_ = list
