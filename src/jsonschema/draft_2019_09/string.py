from jsonschema.common import AValidator, ValidationResult

from .common import Max, Min


class MaxLength(Max):
    pass


class MinLength(Min):
    pass


class Pattern(AValidator):
    def __init__(self, value):
        import re
        self.regex = re.compile(value)

    def validate(self, instance):
        if not self.regex.match(instance):
            return ValidationResult(ok=False, messages=["instance doesn't match the pattern given"])
        return ValidationResult(ok=True)


class String(AValidator):
    def __init__(self, **kwargs):
        self._validators = []
        keyword_to_validator = {
            'minLength': MinLength,
            'maxLength': MaxLength,
            'pattern': Pattern,
        }
        for keyword in keyword_to_validator:
            if kwargs.get(keyword) is not None:
                self._validators.append(
                    keyword_to_validator[keyword](value=kwargs.get(keyword))
                )

    def validate(self, instance):
        results = []
        messages = []
        if not isinstance(instance, str):
            messages.append('instance is not a string')
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
