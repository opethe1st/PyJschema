import unittest

from .primitives import AcceptAll, Const, Enum, RejectAll

from pyjschema.utils import OUTPUT

OUTPUT.set({"errors": []})


class TestAcceptAll(unittest.TestCase):
    def test(self):
        validator = AcceptAll(schema={}, location="", parent=None)
        assert validator(instance=5, location="")


class TestRejectAll(unittest.TestCase):
    def test(self):
        validator = RejectAll(schema={}, location="", parent=None)
        assert not validator(instance=2, location="")


class TestConst(unittest.TestCase):
    def test_const_true(self):
        validator = Const(schema={"const": 5432}, location="", parent=None)
        assert validator(instance=5432, location="")

    def test_const_false(self):
        validator = Const(schema={"const": 12434}, location="", parent=None)
        assert not validator(instance="astring", location="")


class TestEnum(unittest.TestCase):
    def test_const_true(self):
        validator = Enum(
            schema={"enum": [5432, "a string", [], {}]}, location="", parent=None
        )
        assert validator(instance="a string", location="")

    def test_const_false(self):
        validator = Enum(schema={"enum": [12434]}, location="", parent=None)
        assert not validator(instance="astring", location="")
