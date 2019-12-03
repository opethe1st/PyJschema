import itertools
import re

from jschema.common import Dict, KeywordGroup, ValidationError

from .common import validate_max, validate_min
from .type_ import Type


class _Property(KeywordGroup):
    def __init__(
        self,
        schema: Dict,
    ):
        from jschema.draft_2019_09 import build_validator

        properties = schema.get("properties")
        additionalProperties = schema.get("additionalProperties")
        patternProperties = schema.get("patternProperties")
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

        errors = _validate(
            property_validators=self._validators,
            additional_validator=self._additional_validator,
            pattern_validators=self._pattern_validators,
            instance=instance,
        )
        first_result = next(errors, True)
        if first_result:
            return True
        else:
            return ValidationError(children=itertools.chain([first_result], errors))

    def subschema_validators(self):
        yield from self._validators.values()
        if self._additional_validator:
            yield self._additional_validator
        yield from self._pattern_validators.values()


def _validate(property_validators, additional_validator, pattern_validators, instance):
    for key in property_validators:
        if key in instance:
            result = property_validators[key].validate(instance[key])

            if not result:
                yield result

    remaining_properties = set(instance.keys())

    properties_validated_by_pattern = set()
    for regex in pattern_validators:
        for key in remaining_properties:
            if regex.search(key):
                properties_validated_by_pattern.add(key)
                result = pattern_validators[regex].validate(instance[key])
                if not result:
                    yield result

    # additionalProperties only applies to properties not in properties or patternProperties
    additionalProperties = (
        remaining_properties - properties_validated_by_pattern
    ) - set(property_validators.keys())

    if additional_validator:
        for key in additionalProperties:
            result = additional_validator.validate(instance[key])
            if not result:
                yield result


class _Required(KeywordGroup):
    def __init__(self, schema: Dict):
        required = schema["required"]
        self.value = [item.value for item in required]

    def validate(self, instance):
        messages = []
        if set(self.value) - set(instance.keys()):
            messages.append(
                f"There are some missing required fields: {set(self.value) - set(instance.keys())}"
            )

        if not messages:
            return True
        else:
            return ValidationError(messages=messages)


class _PropertyNames(KeywordGroup):
    def __init__(self, schema: Dict):
        # add this to make sure that the type is string - I have seen it missing from
        # examples in the documentation so can only assume it's allowed
        from jschema.draft_2019_09 import build_validator

        propertyNames = schema["propertyNames"]
        self._validator = build_validator(schema=propertyNames)

    def validate(self, instance):
        errors = validate_property_names(validator=self._validator, instance=instance)
        first_result = next(errors, True)
        if first_result:
            return True
        else:
            return ValidationError(children=itertools.chain([first_result], errors))

    def subschema_validators(self):
        yield self._validator


def validate_property_names(validator, instance):
    for propertyName in instance:
        res = validator.validate(propertyName)

        if not res:
            yield res


class _MinProperties(KeywordGroup):
    def __init__(self, schema: Dict):
        self.value = schema["minProperties"].value

    def validate(self, instance):
        return validate_min(instance=instance, value=self.value)


class _MaxProperties(KeywordGroup):
    def __init__(self, schema: Dict):
        self.value = schema["maxProperties"].value

    def validate(self, instance):
        return validate_max(instance=instance, value=self.value)


class _DependentRequired(KeywordGroup):
    def __init__(self, schema: Dict):
        dependentRequired = schema["dependentRequired"]
        self.dependentRequired = {
            key: [val.value for val in value]
            for key, value in dependentRequired.items()
        }

    def validate(self, instance):
        for prop, dependentProperties in self.dependentRequired.items():
            if prop in instance:
                if not (set(dependentProperties) < set(instance.keys())):
                    return ValidationError()
        return True


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
        if res:
            keyTypes = set(type(key) for key in instance)
            if keyTypes:
                # TODO(ope) this seems wrong to me
                if len(keyTypes) != 1 or not (str in keyTypes):
                    messages = ["all the keys of the object need to be strings"]
                    return ValidationError(messages=messages)
            return res
        else:
            return res
