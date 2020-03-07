import unittest

from .primitives import AcceptAll, Const, Enum, RejectAll

from pyjschema.utils import OUTPUT

OUTPUT.set({"errors": []})


class TestAcceptAll(unittest.TestCase):
    def test(self):
        validator = AcceptAll(schema={})
        assert validator(instance=5)


class TestRejectAll(unittest.TestCase):
    def test(self):
        validator = RejectAll(schema={})
        assert not validator(instance=2)


class TestConst(unittest.TestCase):
    def test_const_true(self):
        validator = Const(schema={"const": 5432}, location, parent)
        assert validator(instance=5432)

    def test_const_false(self):
        validator = Const(schema={"const": 12434}, location, parent)
        assert not validator(instance="astring")


class TestEnum(unittest.TestCase):
    def test_const_true(self):
        validator = Enum(
            schema={"enum": [5432, "a string", [], {}]}, location, parent
        )
        assert validator(instance="a string")

    def test_const_false(self):
        validator = Enum(schema={"enum": [12434]}, location, parent)
        assert not validator(instance="astring")
