from pyjschema.common import AValidator, Keyword, ValidationError


class Const(Keyword):
    keyword = "const"

    def validate(self, instance):
        ok = equals(self.value, instance)
        return True if ok else ValidationError()


class Enum(Keyword):
    keyword = "enum"

    def validate(self, instance):
        for value in self.value:
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
    def __init__(self, schema=None, location=None, parent=None):
        self.location = location

    def validate(self, instance):
        return True

    def __repr__(self):
        return "AcceptAll()"


class RejectAll(AValidator):
    def __init__(self, schema=None, location=None, parent=None):
        self.location = location

    def validate(self, instance):
        return ValidationError(messages=["This fails for every value"])

    def __repr__(self):
        return "RejectAll()"
