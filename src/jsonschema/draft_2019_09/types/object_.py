import re
import typing as t

from jsonschema.common import Instance, Keyword, KeywordGroup, Type, ValidationResult

from .common import Max, Min


class _Property(KeywordGroup):
    def __init__(
        self,
        properties: t.Optional[Instance] = None,
        additionalProperties: t.Optional[Instance] = None,
        patternProperties: t.Optional[Instance] = None,
    ):
        from jsonschema.draft_2019_09.validator import build_validator

        self._validators = (
            {key: build_validator(prop) for key, prop in properties.value.items()}
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
                re_compile(key): build_validator(schema=properties)
                for key, properties in patternProperties.value.items()
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
    def __init__(self, required: Instance):
        self.value = [item.value for item in required.value]

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
    def __init__(self, propertyNames: Instance):
        # add this to make sure that the type is string - I have seen it missing from
        # examples in the documentation so can only assume it's allowed
        from jsonschema.draft_2019_09.validator import build_validator

        propertyNames.value["type"] = Instance(value="string", location="")
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


class _MinProperties(Min):
    def __init__(self, minProperties: Instance):
        self.value = minProperties.value


class _MaxProperties(Max):
    def __init__(self, maxProperties: Instance):
        self.value = maxProperties.value


class _DependentRequired(Keyword):
    def __init__(self, dependentRequired: Instance):
        self.dependentRequired = {
            key: [val.value for val in value.value]
            for key, value in dependentRequired.value.items()
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


# TODO(ope): needs a better name
def re_compile(pattern):
    if pattern.startswith("^"):
        value = pattern
    else:
        value = ".*"+pattern
    return re.compile(value)
