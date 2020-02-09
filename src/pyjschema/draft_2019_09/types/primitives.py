from pyjschema.common import AValidator, KeywordGroup, ValidationError


class Const(KeywordGroup):
    def __init__(self, schema: dict, location=None):
        super().__init__(schema=schema, location=location)
        const = schema["const"]
        self.value = (const)

    def validate(self, instance):
        ok = equals(self.value, instance)
        return True if ok else ValidationError()


class Enum(KeywordGroup):
    def __init__(self, schema: dict, location=None):
        super().__init__(schema=schema, location=location)
        enum = schema["enum"]
        self._values = enum

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
    def __init__(self, schema=None, location=None):
        self.location = location

    def validate(self, instance):
        return True


class RejectAll(AValidator):
    def __init__(self, schema=None, location=None):
        self.location = location

    def validate(self, instance):
        return ValidationError(messages=["This fails for every value"])
