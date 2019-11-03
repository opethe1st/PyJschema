from jsonschema.common import AValidator, Instance, Keyword, Type, ValidationResult
from jsonschema.common.annotate import deannotate


class Boolean(Type):
    type_ = bool

    def validate(self, instance):
        # is this faster than an isinstance check?
        res = super().validate(instance=instance)
        if res.ok:
            if (instance is True) or (instance is False):
                return ValidationResult(ok=True)
            else:
                return ValidationResult(
                    ok=False, messages=["instance is not a valid boolean"]
                )
        else:
            return res


class Null(Type):
    type_ = type(None)


class Const(Keyword):
    def __init__(self, const: Instance):
        self.value = deannotate(const)
        self.location = const.location

    def validate(self, instance):
        # these special rules are required because bool is a number and that messes up the
        # type checks
        if isinstance(instance, bool) and isinstance(self.value, bool):
            if instance == self.value:
                return ValidationResult(ok=True)
            else:
                return ValidationResult(ok=False)
        if isinstance(instance, bool) and isinstance(self.value, (int, float)):
            return ValidationResult(ok=False)
        if isinstance(self.value, bool) and isinstance(instance, (int, float)):
            return ValidationResult(ok=False)

        if instance == self.value:
            return ValidationResult(ok=True)
        else:
            # TODO I should add message
            return ValidationResult(ok=False)


class Enum(Keyword):
    def __init__(self, enum: Instance):
        self.location = enum.location
        self._values_validators = [Const(const=item) for item in enum.value]

    def validate(self, instance):
        for validator in self._values_validators:
            res = validator.validate(instance=instance)
            if res.ok:
                return res
            # TODO I should add message
        return ValidationResult(ok=False)


class AcceptAll(AValidator):
    def validate(self, instance):
        return ValidationResult(ok=True)


class RejectAll(AValidator):
    def validate(self, instance):
        return ValidationResult(ok=False, messages=["This fails for every value"])
