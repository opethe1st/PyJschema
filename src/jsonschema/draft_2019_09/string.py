from jsonschema.common import Keyword, Type, ValidationResult

from .common import Max, Min


class _MaxLength(Max):
    pass


class _MinLength(Min):
    pass


class _Pattern(Keyword):
    def __init__(self, value):
        import re
        self.regex = re.compile(value)

    def validate(self, instance):
        if not self.regex.match(instance):
            return ValidationResult(ok=False, messages=["instance doesn't match the pattern given"])
        return ValidationResult(ok=True)


class String(Type):
    KEYWORD_TO_VALIDATOR = {
        'minLength': _MinLength,
        'maxLength': _MaxLength,
        'pattern': _Pattern,
    }

    def __init__(self, **kwargs):
        self._validators = []
        for keyword in self.KEYWORD_TO_VALIDATOR:
            if kwargs.get(keyword) is not None:
                self._validators.append(
                    self.KEYWORD_TO_VALIDATOR[keyword](value=kwargs.get(keyword))
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
