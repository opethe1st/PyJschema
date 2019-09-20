
from jsonschema.common import (
    Keyword,
    KeywordGroup,
    Type,
    ValidationResult
)

from .common import Max, Min


class Property(KeywordGroup):

    def __init__(self, value=None, additionalProperties=None, patternProperties=None, **kwargs):
        import re
        from .validator import build_validator

        self._validators = {key: build_validator(value) for key, value in value.items()} if value else {}
        self._additional_validator = build_validator(additionalProperties) if additionalProperties is not None else None
        self._pattern_validators = {
            re.compile(key): build_validator(value) for key, value in patternProperties.items()
        } if patternProperties else {}

    def validate(self, instance):
        results = []
        messages = []

        for key in self._validators:
            if key in instance:
                result = self._validators[key].validate(instance[key])

                if not result.ok:
                    results.append(result)

        additionalProperties = set(instance.keys()) - set(self._validators.keys())

        properties_validated_by_pattern = set()
        for regex in self._pattern_validators:
            for key in additionalProperties:
                if regex.match(key):
                    properties_validated_by_pattern.add(key)
                    result = self._pattern_validators[regex].validate(instance[key])
                    if not result.ok:
                        results.append(result)

        # additionalProperties only applies to properties not in properties or patternProperties
        additionalProperties -= properties_validated_by_pattern
        if self._additional_validator:
            for key in additionalProperties:
                result = self._additional_validator.validate(instance[key])
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
        validators = list(self._validators.values())
        if self._additional_validator:
            validators.append(self._additional_validator)
        validators.extend(self._pattern_validators.values())
        return validators


class Required(Keyword):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        messages = []
        if (set(self.value) - set(instance.keys())):
            messages.append(f"There are some missing required fields: {set(self.value) - set(instance.keys())}")

        if not messages:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(ok=False, messages=messages)


class PropertyNames(Keyword):
    def __init__(self, schema):
        # add this to make sure that the type is string - I have seen it missing from
        # examples in the documentation so can only assume it's allowed
        from .validator import build_validator

        schema["type"] = "string"
        self._validator = build_validator(schema)

    def validate(self, instance):
        children = []
        for propertyName in instance:
            res = self._validator.validate(propertyName)

            if not res.ok:
                children.append(res)

        if not children:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(ok=False, children=children)

    def subschema_validators(self):
        return [self._validator]


class MinProperties(Min):
    pass


class MaxProperties(Max):
    pass


class Object(Type):
    keyword_to_validator = {
        "required": Required,
        "propertyNames": PropertyNames,
        "minProperties": MinProperties,
        "maxProperties": MaxProperties,
    }

    def __init__(self, **kwargs):
        self._validators = []
        for keyword in self.keyword_to_validator:

            if kwargs.get(keyword) is not None:
                self._validators.append(
                    self.keyword_to_validator[keyword](kwargs.get(keyword))
                )

        if (
            kwargs.get("properties") is not None
            or kwargs.get("patternProperties") is not None
            or kwargs.get("additionalProperties") is not None
        ):
            self._validators.append(
                Property(
                    value=kwargs.get("properties"),
                    additionalProperties=kwargs.get("additionalProperties"),
                    patternProperties=kwargs.get("patternProperties")
                )
            )

    def validate(self, instance):
        results = []
        messages = []
        if not isinstance(instance, dict):
            messages.append('instance is not a dictionary')

        keyTypes = set(type(key) for key in instance)
        if keyTypes:
            if len(keyTypes) != 1 or not (str in keyTypes):
                messages.append('all the keys of the object need to be strings')

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
        return self._validators
