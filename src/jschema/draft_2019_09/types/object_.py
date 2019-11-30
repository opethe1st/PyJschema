import itertools
import re
import typing as t

from jschema.common import Dict, KeywordGroup, List, Primitive, ValidationError

from .common import validate_max, validate_min
from .type_base import Type


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

        errors = _validate(
            property_validators=self._validators,
            additional_validator=self._additional_validator,
            pattern_validators=self._pattern_validators,
            instance=instance,
        )
        first_error = next(errors, True)
        if first_error:
            return True
        else:
            return ValidationError(children=itertools.chain([first_error], errors))

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
    def __init__(self, required: List):
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
    def __init__(self, propertyNames: Dict):
        # add this to make sure that the type is string - I have seen it missing from
        # examples in the documentation so can only assume it's allowed
        from jschema.draft_2019_09 import build_validator

        self._validator = build_validator(schema=propertyNames)

    def validate(self, instance):
        errors = yield_property_name_errors(
            validator=self._validator, instance=instance
        )
        first_error = next(errors, True)
        if first_error:
            return True
        else:
            return ValidationError(children=itertools.chain([first_error], errors))

    def subschema_validators(self):
        yield self._validator


def yield_property_name_errors(validator, instance):
    for propertyName in instance:
        res = validator.validate(propertyName)

        if not res:
            yield res


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
                    messages = "all the keys of the object need to be strings"
                    return ValidationError(messages=messages)
            return res
        else:
            return res
