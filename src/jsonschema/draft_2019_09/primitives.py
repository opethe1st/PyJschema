from jsonschema.common import (
    AValidator,
    Keyword,
    Type,
    ValidationResult
)


class Boolean(Type):

    def validate(self, instance):
        # is this faster than an isinstance check?
        if (instance is True) or (instance is False):
            return ValidationResult(ok=True)
        else:
            return ValidationResult(ok=False, messages=['instance is not a valid boolean'])


class Null(Type):

    def validate(self, instance):
        if instance is None:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(ok=False)


class Const(Keyword):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        if instance == self.value:
            return ValidationResult(ok=True)
        else:
            # TODO I should add message
            return ValidationResult(ok=False)


class Enum(Keyword):
    def __init__(self, values):
        self.values = values

    def validate(self, instance):
        if instance in self.values:
            return ValidationResult(ok=True)
        else:
            # TODO I should add message
            return ValidationResult(ok=False)


class AcceptAll(AValidator):

    def validate(self, instance):
        return ValidationResult(ok=True)


class RejectAll(AValidator):

    def validate(self, instance):
        return ValidationResult(ok=False, messages=["This fails for every value"])
