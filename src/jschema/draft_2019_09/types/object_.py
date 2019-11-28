import re
import typing as t

from jschema.common import Primitive, List, Dict, KeywordGroup, Type, ValidationResult

from .common import validate_max, validate_min


class _Property(KeywordGroup):
    def __init__(
        self,
        properties: t.Optional[Dict] = None,
        additionalProperties: t.Optional[Dict] = None,
        patternProperties: t.Optional[Dict] = None,
    ):
        from jschema.draft_2019_09 import build_validator

        self._validators = (
            {key: build_validator(prop) for key, prop in properties.items()}
            if properties
            else {}
        )
        self._additional_validator = (
            build_validator(schema=additionalProperties)
            if additionalProperties is not None
            else None
        )
        self._pattern_validators = (
            {
                re.compile(key): build_validator(schema=properties)
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

        remaining_properties = set(instance.keys())

        properties_validated_by_pattern = set()
        for regex in self._pattern_validators:
            for key in remaining_properties:
                if regex.search(key):
                    properties_validated_by_pattern.add(key)
                    result = self._pattern_validators[regex].validate(instance[key])
                    if not result.ok:
                        results.append(result)

        # additionalProperties only applies to properties not in properties or patternProperties
        additionalProperties = (
            remaining_properties - properties_validated_by_pattern
        ) - set(self._validators.keys())
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


class _Required(KeywordGroup):
    def __init__(self, required: List):
        self.value = [item.value for item in required]

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


class _PropertyNames(KeywordGroup):
    def __init__(self, propertyNames: Dict):
        # add this to make sure that the type is string - I have seen it missing from
        # examples in the documentation so can only assume it's allowed
        from jschema.draft_2019_09 import build_validator

        self._validator = build_validator(schema=propertyNames)

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


class _MinProperties(KeywordGroup):
    def __init__(self, minProperties: Primitive):
        self.value = minProperties.value

    def validate(self, instance):
        return validate_min(instance=instance, value=self.value)


class _MaxProperties(KeywordGroup):
    def __init__(self, maxProperties: Primitive):
        self.value = maxProperties.value

    def validate(self, instance):
        return validate_max(instance=instance, value=self.value)


class _DependentRequired(KeywordGroup):
    def __init__(self, dependentRequired: Dict):
        self.dependentRequired = {
            key: [val.value for val in value]
            for key, value in dependentRequired.items()
        }

    def validate(self, instance):
        for prop, dependentProperties in self.dependentRequired.items():
            if prop in instance:
                if not (set(dependentProperties) < set(instance.keys())):
                    return ValidationResult(ok=False)
        return ValidationResult(ok=True)


class Object(Type):
    KEYWORDS_TO_VALIDATOR = {
        ("required",): _Required,
        ("propertyNames",): _PropertyNames,
        ("minProperties",): _MinProperties,
        ("maxProperties",): _MaxProperties,
        ("dependentRequired",): _DependentRequired,
        ("properties", "patternProperties", "additionalProperties"): _Property,
    }
    type_ = dict

    def validate(self, instance):
        res = super().validate(instance=instance)
        if res.ok:
            keyTypes = set(type(key) for key in instance)
            if keyTypes:
                # TODO(ope) this seems wrong to me
                if len(keyTypes) != 1 or not (str in keyTypes):
                    res.messages.append("all the keys of the object need to be strings")
                    return ValidationResult(ok=False, messages=res.messages)
            return res
        else:
            return res
