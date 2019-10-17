
from jsonschema.common import Keyword, KeywordGroup, Type, ValidationResult

from .common import Max, Min


class _ItemsArray(KeywordGroup):
    def __init__(self, item_schema, additional_items_schema=None, **kwargs):
        from .validator import build_validator

        self.item_validators = [build_validator(schema) for schema in item_schema]
        self.additional_item_validator = build_validator(additional_items_schema) if additional_items_schema else None

    def validate(self, instance):
        children = []

        i = 0
        while i < len(self.item_validators):
            if i >= len(instance):
                break

            res = self.item_validators[i].validate(instance[i])

            if not res.ok:
                children.append(res)

            i += 1

        # additionalItem for the rest of the items in the instance
        if self.additional_item_validator:
            while i < len(instance):
                res = self.additional_item_validator.validate(instance[i])

                if not res.ok:
                    children.append(res)

                i += 1

        if children:
            return ValidationResult(ok=False, children=children)
        else:
            return ValidationResult(ok=True)

    def subschema_validators(self):
        validators = self.item_validators[:]

        if self.additional_item_validator:
            validators.append(self.additional_item_validator)

        return validators


class _Items(Keyword):
    def __init__(self, item_schema, **kwargs):
        from .validator import build_validator

        self._validator = build_validator(item_schema)

    def validate(self, instance):
        children = []

        for value in instance:
            res = self._validator.validate(value)

            if not res.ok:
                children.append(res)

        if not children:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(ok=False, children=children)

    def subschema_validators(self):
        return [self._validator]


class _Contains(Keyword):
    def __init__(self, schema, **kwargs):
        from .validator import build_validator

        self._validator = build_validator(schema)

    def validate(self, instance):

        for value in instance:
            res = self._validator.validate(value)

            if res.ok:
                return ValidationResult(ok=True)

        return ValidationResult(
            ok=False,
            messages=["No item in this array matches the schema in the contains keyword"]
        )

    def subschema_validators(self):
        return [self._validator]


class _MinItems(Min):
    pass


class _MaxItems(Max):
    pass


class _UniqueItems(Keyword):
    def __init__(self, value: bool):
        self.value = value

    def validate(self, instance):
        if self.value:
            itemsset = set([str(value) for value in instance])

            if len(itemsset) != len(instance):
                return ValidationResult(ok=False)
            # TODO(ope) - actually make sure the values are unique

        return ValidationResult(ok=True)


class Array(Type):

    KEYWORD_TO_VALIDATOR = {
        'minItems': _MinItems,
        'maxItems': _MaxItems,
        'uniqueItems': _UniqueItems,
        'contains': _Contains,
    }

    def __init__(self, **kwargs):
        self._validators = []

        for keyword in self.KEYWORD_TO_VALIDATOR:

            if kwargs.get(keyword) is not None:
                self._validators.append(
                    self.KEYWORD_TO_VALIDATOR[keyword](kwargs.get(keyword))
                )

        if 'items' in kwargs:

            if isinstance(kwargs['items'], list):
                items_validator = _ItemsArray(item_schema=kwargs['items'], additional_items_schema=kwargs.get('additionalItems'))
            else:
                items_validator = _Items(item_schema=kwargs['items'])

            self._validators.append(items_validator)

    def validate(self, instance):
        results = []
        messages = []

        if not isinstance(instance, list):
            messages.append('instance is not a list')

        for validator in self._validators:
            result = validator.validate(instance)

            if not result.ok:
                results.append(result)

        if not results and not messages:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(
                ok=False,
                messages=messages,
                children=results
            )

    def subschema_validators(self):
        # maybe optimize by not returning validators that don't have schemas embedded
        return self._validators
