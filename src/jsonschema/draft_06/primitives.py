from jsonschema.common import ValidationResult

from .i_validator import AValidator


class Boolean(AValidator):

    def validate(self, instance):
        # is this faster than an isinstance check?
        if (instance is True) or (instance is False):
            return ValidationResult(ok=True)
        else:
            return ValidationResult(ok=False, messages=['instance is not a valid boolean'])


class Null(AValidator):

    def validate(self, instance):
        if instance is None:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(ok=False)


class AcceptAll(AValidator):

    def validate(self, instance):
        return ValidationResult(ok=True)


class RejectAll(AValidator):

    def validate(self, instance):
        return ValidationResult(ok=False, messages=["This fails for every value"])
