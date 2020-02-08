import unittest

from .primitives import AcceptAll, Const, Enum, RejectAll


class TestAcceptAll(unittest.TestCase):
    def test(self):
        validator = AcceptAll(schema={})
        assert validator.validate(instance=5)


class TestRejectAll(unittest.TestCase):
    def test(self):
        validator = RejectAll(schema={})
        assert not validator.validate(instance=2)


class TestConst(unittest.TestCase):
    def test_const_true(self):
        validator = Const(schema={"const": 5432})
        assert validator.validate(instance=5432)

    def test_const_false(self):
        validator = Const(schema={"const": 12434})
        assert not validator.validate(instance="astring")


class TestEnum(unittest.TestCase):
    def test_const_true(self):
        validator = Enum(schema={"enum": [5432, "a string", [], {}]})
        assert validator.validate(instance="a string")

    def test_const_false(self):
        validator = Enum(schema={"enum": [12434]})
        assert not validator.validate(instance="astring")
