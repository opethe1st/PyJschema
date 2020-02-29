from pyjschema.common import AValidator, Keyword
from pyjschema.utils import basic_output


class Const(Keyword):
    keyword = "const"

    @basic_output("this instance {instance} is not equal to the constant {self.value}")
    def __call__(self, instance, output, location=None):
        ok = equals(self.value, instance)
        return True if ok else False


class Enum(Keyword):
    keyword = "enum"

    @basic_output("this instance {instance} is not part of this enum {value}")
    def __call__(self, instance, output, location=None):
        for value in self.value:
            if equals(value, instance):
                return True
        return False


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

    def __call__(self, instance, output, location=None):
        return True

    def __repr__(self):
        return "AcceptAll()"


class RejectAll(AValidator):
    def __init__(self, schema=None, location=None, parent=None):
        self.location = location

    @basic_output("this fails for every instance")
    def __call__(self, instance, output, location=None):
        return False

    def __repr__(self):
        return "RejectAll()"
