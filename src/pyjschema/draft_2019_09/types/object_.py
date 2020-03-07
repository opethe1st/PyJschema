import re

from pyjschema.common import Keyword, KeywordGroup
from pyjschema.draft_2019_09.context import BUILD_VALIDATOR
from pyjschema.utils import validate_only, ValidationResult


class _Property(KeywordGroup):
    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        build_validator = BUILD_VALIDATOR.get()

        properties = schema.get("properties")
        additionalProperties = schema.get("additionalProperties")
        patternProperties = schema.get("patternProperties")
        self._validators = (
            {
                key: build_validator(
                    schema=prop, location=f"{location}/properties/{key}", parent=self
                )
                for key, prop in properties.items()
            }
            if properties
            else {}
        )
        self._additional_validator = (
            build_validator(
                schema=additionalProperties,
                location=f"{location}/additionalProperties",
                parent=self,
            )
            if additionalProperties is not None
            else None
        )
        self._pattern_validators = (
            {
                re.compile(key): build_validator(
                    schema=properties,
                    location=f"{location}/patternProperties/{key}",
                    parent=self,
                )
                for key, properties in patternProperties.items()
            }
            if patternProperties
            else {}
        )

    @validate_only(type_=dict)
    def __call__(self, instance, location=None):

        results = _validate(
            property_validators=self._validators,
            additional_validator=self._additional_validator,
            pattern_validators=self._pattern_validators,
            instance=instance,
            location=location,
        )
        results = list(results)
        if all(results):
            return True
        else:
            return ValidationResult(
                message=f"This instance fails the combination of properties, patternProperties and additionalProperties",
                location=location,
                keywordLocation=self.location,
                sub_results=results,
            )

    def __repr__(self):
        return f"Property(properties={self._validators}, additionalProperties={self._additional_validator}, patternProperties={self._pattern_validators})"

    def sub_validators(self):
        yield from self._validators.values()
        if self._additional_validator:
            yield self._additional_validator
        yield from self._pattern_validators.values()


def _validate(
    property_validators, additional_validator, pattern_validators, instance, location,
):

    for key in property_validators:
        if key in instance:
            result = property_validators[key](
                instance=instance[key], location=f"{location}/{key}"
            )

            if not result:
                yield result

    remaining_properties = set(instance.keys())

    properties_validated_by_pattern = set()
    for regex in pattern_validators:
        for key in remaining_properties:
            if regex.search(key):
                properties_validated_by_pattern.add(key)
                result = pattern_validators[regex](
                    instance=instance[key], location=location
                )  # this is wrong. should be location/regex fix later
                if not result:
                    yield result

    # additionalProperties only applies to properties not in properties or patternProperties
    additionalProperties = (
        remaining_properties - properties_validated_by_pattern
    ) - set(property_validators.keys())

    if additional_validator:
        for key in additionalProperties:
            result = additional_validator(
                instance=instance[key], location=f"{location}/{key}"
            )
            if not result:
                yield result


class _Required(Keyword):
    keyword = "required"

    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        required = schema["required"]
        self.value = required

    @validate_only(type_=dict)
    def __call__(self, instance, location=None):
        missing = set(self.value) - set(instance.keys())
        if missing:
            return ValidationResult(
                message=f"This instance is missing these required keys: {missing}",
                location=location,
                keywordLocation=self.location,
            )
        return True


class _PropertyNames(Keyword):
    keyword = "propertyNames"

    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        # add this to make sure that the type is string - I have seen it missing from
        # examples in the documentation so can only assume it's allowed
        build_validator = BUILD_VALIDATOR.get()

        self._validator = build_validator(schema=self.value, location=self.location)

    @validate_only(type_=dict)
    def __call__(self, instance, location=None):
        results = validate_property_names(
            validator=self._validator, instance=instance, location=location
        )
        results = list(results)
        if all(results):
            return True
        else:
            return ValidationResult(
                message="Not all property names match this schema",
                location=location,
                keywordLocation=self.location,
                sub_results=results,
            )

    def sub_validators(self):
        yield self._validator


def validate_property_names(validator, instance, location):
    for propertyName in instance:
        res = validator(instance=propertyName, location=f"{location}/{propertyName}")

        if not res:
            yield res


class _MinProperties(Keyword):
    keyword = "minProperties"

    @validate_only(type_=dict)
    def __call__(self, instance, location=None):
        res = self.value <= len(instance)
        return (
            True
            if res
            else ValidationResult(
                message=f"this {instance} has less than minProperties: {self.value}",
                keywordLocation=self.location,
                location=location,
            )
        )


class _MaxProperties(Keyword):
    keyword = "maxProperties"

    @validate_only(type_=dict)
    def __call__(self, instance, location=None):
        res = len(instance) <= self.value
        return (
            True
            if res
            else ValidationResult(
                message=f"this {instance} has more than maxProperties: {self.value}",
                keywordLocation=self.location,
                location=location,
            )
        )


class _DependentRequired(Keyword):
    keyword = "dependentRequired"

    @validate_only(type_=dict)
    def __call__(self, instance, location=None):
        results = []
        for prop, dependentProperties in self.value.items():
            if prop in instance:
                if not (set(dependentProperties) < set(instance.keys())):
                    # need to fill in the message
                    results.append(
                        ValidationResult(
                            message="", location=location, keywordLocation=self.location
                        )
                    )

        # need to fill in message
        return (
            True
            if not results
            else ValidationResult(
                message="", keywordLocation=self.location, location=location
            )
        )
