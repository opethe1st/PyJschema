from jsonschema.common import ValidationResult

from .i_validator import IValidator


class Boolean(IValidator):

    def validate(self, instance):
        # is this faster than an isinstance check?
        if (instance is True) or (instance is False):
            return ValidationResult(ok=True)
        else:
            return ValidationResult(ok=False, messages=['instance is not a valid boolean'])


class Null(IValidator):

    def validate(self, instance):
        if instance is None:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(ok=False)


class AcceptAll(IValidator):

    def validate(self, instance):
        return ValidationResult(ok=True)


class RejectAll(IValidator):

    def validate(self, instance):
        return ValidationResult(ok=False, messages=["This fails for every value"])
