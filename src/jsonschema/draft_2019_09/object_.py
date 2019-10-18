import re
import typing as t

from jsonschema.common import Keyword, KeywordGroup, Schema, Type, ValidationResult

from .common import Max, Min


class _Property(KeywordGroup):
    def __init__(
        self,
        properties: t.Optional[Schema],
        additionalProperties: t.Optional[Schema],
        patternProperties=t.Optional[Schema],
    ):
        from .validator import build_validator

        self._validators = (
            {key: build_validator(prop) for key, prop in properties.items()}
            if properties
            else {}
        )
        self._additional_validator = (
            build_validator(additionalProperties)
            if additionalProperties is not None
            else None
        )
        self._pattern_validators = (
            {
                re.compile(key): build_validator(properties)
                for key, properties in patternProperties.items()
            }
            if patternProperties
            else {}
        )

    def validate(self, instance):
        results = []
        messages = []

        for key in self._validators:
            if key in instance:
                result = self._validators[key].validate(instance[key])

                if not result.ok:
                    results.append(result)

        remaining_properties = set(instance.keys()) - set(self._validators.keys())

        properties_validated_by_pattern = set()
        for regex in self._pattern_validators:
            for key in remaining_properties:
                if regex.match(key):
                    properties_validated_by_pattern.add(key)
                    result = self._pattern_validators[regex].validate(instance[key])
                    if not result.ok:
                        results.append(result)

        # additionalProperties only applies to properties not in properties or patternProperties
        additionalProperties = remaining_properties - properties_validated_by_pattern
        if self._additional_validator:
            for key in additionalProperties:
                result = self._additional_validator.validate(instance[key])
                if not result.ok:
                    results.append(result)

        if not results and not messages:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(ok=False, messages=messages, children=results)

    def subschema_validators(self):
        for validator in self._validators.values():
            yield validator
        if self._additional_validator:
            yield self._additional_validator
        for validator in self._pattern_validators.values():
            yield validator


class _Required(Keyword):
    def __init__(self, required: t.List[str]):
        self.value = required

    def validate(self, instance):
        messages = []
        if set(self.value) - set(instance.keys()):
            messages.append(
                f"There are some missing required fields: {set(self.value) - set(instance.keys())}"
            )

        if not messages:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(ok=False, messages=messages)


class _PropertyNames(Keyword):
    def __init__(self, propertyNames: Schema):
        # add this to make sure that the type is string - I have seen it missing from
        # examples in the documentation so can only assume it's allowed
        from .validator import build_validator

        propertyNames["type"] = "string"
        self._validator = build_validator(propertyNames)

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
        yield self._validator


class _MinProperties(Min):
    def __init__(self, minProperties: int):
        self.value = minProperties


class _MaxProperties(Max):
    def __init__(self, maxProperties: int):
        self.value = maxProperties


class Object(Type):
    KEYWORDS_TO_VALIDATOR = {
        ("required",): _Required,
        ("propertyNames",): _PropertyNames,
        ("minProperties",): _MinProperties,
        ("maxProperties",): _MaxProperties,
        ("properties", "patternProperties", "additionalProperties"): _Property,
    }
    type_ = dict

    def validate(self, instance):
        res = super().validate(instance=instance)

        keyTypes = set(type(key) for key in instance)
        if keyTypes:
            # TODO(ope) this seems wrong to me
            if len(keyTypes) != 1 or not (str in keyTypes):
                res.messages.append("all the keys of the object need to be strings")
                return ValidationResult(ok=False, messages=res.messages)
        return res
