from jschema.common import AValidator, Dict, KeywordGroup, Primitive, ValidationError
from jschema.common.annotate import deannotate

from .type_base import Type


class Boolean(Type):
    type_ = bool

    def validate(self, instance):
        # is this faster than an isinstance check?
        res = super().validate(instance=instance)
        if res:
            if (instance is True) or (instance is False):
                return True
            else:
                return ValidationError(messages=["instance is not a valid boolean"])
        else:
            return res


class Null(Type):
    type_ = type(None)


class Const(KeywordGroup):
    def __init__(self, schema: Dict):
        const = schema["const"]
        self.value = deannotate(const)

    def validate(self, instance):
        ok = equals(self.value, instance)
        return True if ok else ValidationError()


class Enum(KeywordGroup):
    def __init__(self, schema: Dict):
        enum = schema["enum"]
        self._values = [deannotate(instance=instance) for instance in enum]

    def validate(self, instance):
        for value in self._values:
            if equals(value, instance):
                return True
        return ValidationError()


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
    def __init__(self, schema: Primitive):
        self.location = schema.location.rstrip("#")

    def validate(self, instance):
        return True


class RejectAll(AValidator):
    def __init__(self, schema: Primitive):
        self.location = schema.location.rstrip("#")

    def validate(self, instance):
        return ValidationError(messages=["This fails for every value"])
