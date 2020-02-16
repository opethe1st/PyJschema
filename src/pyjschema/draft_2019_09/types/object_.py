import itertools
import re

from pyjschema.common import KeywordGroup, ValidationError

from .common import validate_max, validate_min, correct_type


class _Property(KeywordGroup):
    def __init__(self, schema: dict, location=None, parent=None):
        from pyjschema.draft_2019_09 import build_validator
        self.parent = parent
        properties = schema.get("properties")
        additionalProperties = schema.get("additionalProperties")
        patternProperties = schema.get("patternProperties")
        self._validators = (
            {key: build_validator(schema=prop, location=f"{location}/properties/{key}", parent=self) for key, prop in properties.items()}
            if properties
            else {}
        )
        self._additional_validator = (
            build_validator(schema=additionalProperties, location=f"{location}/additionalProperties", parent=self)
            if additionalProperties is not None
            else None
        )
        self._pattern_validators = (
            {
                re.compile(key): build_validator(schema=properties, location=f"{location}/patternProperties/{key}", parent=self)
                for key, properties in patternProperties.items()
            }
            if patternProperties
            else {}
        )

    @correct_type(type_=dict)
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

    def __repr__(self):
        return f"Property(properties={self._validators}, additionalProperties={self._additional_validator}, patternProperties={self._pattern_validators})"

    def sub_validators(self):
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
    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=f"{location}/required", parent=parent)
        required = schema["required"]
        self.value = required

    @correct_type(type_=dict)
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

    def __repr__(self):
        return f"Required(value={self.value!r})"


class _PropertyNames(KeywordGroup):
    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        # add this to make sure that the type is string - I have seen it missing from
        # examples in the documentation so can only assume it's allowed
        from pyjschema.draft_2019_09 import build_validator

        propertyNames = schema["propertyNames"]
        self._validator = build_validator(schema=propertyNames, location=f"{location}/propertyNames")

    @correct_type(type_=dict)
    def validate(self, instance):
        errors = validate_property_names(validator=self._validator, instance=instance)
        first_result = next(errors, True)
        if first_result:
            return True
        else:
            return ValidationError(children=itertools.chain([first_result], errors))

    def sub_validators(self):
        yield self._validator


def validate_property_names(validator, instance):
    for propertyName in instance:
        res = validator.validate(propertyName)

        if not res:
            yield res


class _MinProperties(KeywordGroup):
    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=self)
        self.value = schema["minProperties"]

    @correct_type(type_=dict)
    def validate(self, instance):
        return validate_min(instance=instance, value=self.value)


class _MaxProperties(KeywordGroup):
    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        self.value = schema["maxProperties"]

    @correct_type(type_=dict)
    def validate(self, instance):
        return validate_max(instance=instance, value=self.value)


class _DependentRequired(KeywordGroup):
    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        dependentRequired = schema["dependentRequired"]
        self.dependentRequired = {
            key: value
            for key, value in dependentRequired.items()
        }

    @correct_type(type_=dict)
    def validate(self, instance):
        for prop, dependentProperties in self.dependentRequired.items():
            if prop in instance:
                if not (set(dependentProperties) < set(instance.keys())):
                    return ValidationError()
        return True
