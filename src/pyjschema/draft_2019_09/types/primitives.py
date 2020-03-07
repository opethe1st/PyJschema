from pyjschema.common import AValidator, Keyword
from pyjschema.utils import ValidationResult


class Const(Keyword):
    keyword = "const"

    def __call__(self, instance, location=None):
        ok = equals(self.value, instance)
        return (
            True
            if ok
            else ValidationResult(
                message=f"{instance!r} is not equal to the constant {self.value!r}",
                location=location,
                keywordLocation=self.location,
            )
        )


class Enum(Keyword):
    keyword = "enum"

    def __call__(self, instance, location=None):
        for value in self.value:
            if equals(value, instance):
                return True
        return ValidationResult(
            message=f"{instance!r} is not one of the values in this enum {self.value!r}",
            location=location,
            keywordLocation=self.location,
        )


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

    def __call__(self, instance, location=""):
        return True

    def __repr__(self):
        return "AcceptAll()"


class RejectAll(AValidator):
    def __init__(self, schema=None, location=None, parent=None):
        self.location = location

    def __call__(self, instance, location=""):
        return ValidationResult(
            message="this fails for every instance",
            location=location,
            keywordLocation=self.location,
        )

    def __repr__(self):
        return "RejectAll()"
