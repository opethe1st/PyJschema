import re

from pyjschema.common import Keyword, KeywordGroup
from pyjschema.draft_2019_09.context import BUILD_VALIDATOR
from pyjschema.utils import basic_output, validate_only

from .common import validate_max, validate_min


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

    @basic_output("This instance: {instance} fails the combination of properties, patternProperties and additionalProperties")
    @validate_only(type_=dict)
    def __call__(self, instance, output, location=None):

        errors = _validate(
            property_validators=self._validators,
            additional_validator=self._additional_validator,
            pattern_validators=self._pattern_validators,
            instance=instance,
            location=location,
            output=output,
        )
        first_result = next(errors, True)
        if first_result:
            return True
        else:
            return False

    def __repr__(self):
        return f"Property(properties={self._validators}, additionalProperties={self._additional_validator}, patternProperties={self._pattern_validators})"

    def sub_validators(self):
        yield from self._validators.values()
        if self._additional_validator:
            yield self._additional_validator
        yield from self._pattern_validators.values()


def _validate(property_validators, additional_validator, pattern_validators, instance, location, output):

    for key in property_validators:
        if key in instance:
            result = property_validators[key](instance=instance[key], output=output, location=f"{location}/{key}")

            if not result:
                yield result

    remaining_properties = set(instance.keys())

    properties_validated_by_pattern = set()
    for regex in pattern_validators:
        for key in remaining_properties:
            if regex.search(key):
                properties_validated_by_pattern.add(key)
                result = pattern_validators[regex](instance=instance[key], output=output, location=location)  # this is wrong. should be location/regex fix later
                if not result:
                    yield result

    # additionalProperties only applies to properties not in properties or patternProperties
    additionalProperties = (
        remaining_properties - properties_validated_by_pattern
    ) - set(property_validators.keys())

    if additional_validator:
        for key in additionalProperties:
            result = additional_validator(instance=instance[key], output=output, location=f"{location}/{key}")
            if not result:
                yield result


class _Required(Keyword):
    keyword = "required"

    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        required = schema["required"]
        self.value = required

    @basic_output("This instance fails required")
    @validate_only(type_=dict)
    def __call__(self, instance, output, location=None):
        if set(self.value) - set(instance.keys()):
            return False
        return True


class _PropertyNames(Keyword):
    keyword = "propertyNames"

    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        # add this to make sure that the type is string - I have seen it missing from
        # examples in the documentation so can only assume it's allowed
        build_validator = BUILD_VALIDATOR.get()

        self._validator = build_validator(schema=self.value, location=self.location)

    @basic_output("Some propertyNames fails")
    @validate_only(type_=dict)
    def __call__(self, instance, output, location=None):
        errors = validate_property_names(validator=self._validator, instance=instance, output=output, location=location)
        first_result = next(errors, True)
        if first_result:
            return True
        else:
            return False

    def sub_validators(self):
        yield self._validator


def validate_property_names(validator, instance, output, location):
    for propertyName in instance:
        res = validator(instance=propertyName, output=output, location=f"{location}/{propertyName}")

        if not res:
            yield res


class _MinProperties(Keyword):
    keyword = "minProperties"

    @basic_output("fails minProperties")
    @validate_only(type_=dict)
    def __call__(self, instance, output, location=None):
        return validate_min(instance=instance, value=self.value)


class _MaxProperties(Keyword):
    keyword = "maxProperties"

    @basic_output("fails maxProperties")
    @validate_only(type_=dict)
    def __call__(self, instance, output, location=None):
        return validate_max(instance=instance, value=self.value)


class _DependentRequired(Keyword):
    keyword = "dependentRequired"

    @basic_output("fails dependentRequired")
    @validate_only(type_=dict)
    def __call__(self, instance, output, location=None):
        for prop, dependentProperties in self.value.items():
            if prop in instance:
                if not (set(dependentProperties) < set(instance.keys())):
                    return False
        return True
