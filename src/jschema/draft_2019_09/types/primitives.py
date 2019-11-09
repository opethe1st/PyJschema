from jschema.common import (
    AValidator,
    Instance,
    Keyword,
    Type,
    ValidationResult
)
from jschema.common.annotate import deannotate


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
    def __init__(self, schema: Instance):
        const = schema.value["const"]
        self.value = deannotate(const)

    def validate(self, instance):
        ok = equals(self.value, instance)
        return ValidationResult(ok=ok)


class Enum(Keyword):
    def __init__(self, schema: Instance):
        enum = schema.value["enum"]
        self._values = [deannotate(instance=instance) for instance in enum.value]

    def validate(self, instance):
        for value in self._values:
            if equals(value, instance):
                return ValidationResult(ok=True)
        return ValidationResult(ok=False)


def equals(a, b):
    # these special rules are required because bool is a number and that messes up the
    # type checks
    if isinstance(a, bool) and isinstance(b, bool):
        return a is b
    if isinstance(a, bool) and isinstance(b, (int, float)):
        return False
    if isinstance(b, bool) and isinstance(a, (int, float)):
        return False

    if a == b:
        return True
    else:
        # TODO I should add message
        return False


class AcceptAll(AValidator):
    def validate(self, instance):
        return ValidationResult(ok=True)


class RejectAll(AValidator):
    def validate(self, instance):
        return ValidationResult(ok=False, messages=["This fails for every value"])
