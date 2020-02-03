import unittest

from pyjschema.common import annotate

from .primitives import AcceptAll, Boolean, Const, Enum, Null, RejectAll


class TestAcceptAll(unittest.TestCase):
    def test(self):
        validator = AcceptAll(schema=annotate({}))
        assert validator.validate(instance=5)


class TestRejectAll(unittest.TestCase):
    def test(self):
        validator = RejectAll(schema=annotate({}))
        assert not validator.validate(instance=2)


class TestBoolean(unittest.TestCase):
    def test_boolean_true(self):
        validator = Boolean(schema=annotate({}))
        assert validator.validate(instance=True)

    def test_boolean_false(self):
        validator = Boolean(schema=annotate({}))
        assert not validator.validate(instance=1234)


class TestNull(unittest.TestCase):
    def test_null_true(self):
        validator = Null(schema=annotate({}))
        assert validator.validate(instance=None)

    def test_null_false(self):
        validator = Null(schema=annotate({}))
        assert not validator.validate(instance="None")


class TestConst(unittest.TestCase):
    def test_const_true(self):
        validator = Const(schema=annotate({"const": 5432}))
        assert validator.validate(instance=5432)

    def test_const_false(self):
        validator = Const(schema=annotate({"const": 12434}))
        assert not validator.validate(instance="astring")


class TestEnum(unittest.TestCase):
    def test_const_true(self):
        validator = Enum(schema=annotate({"enum": [5432, "a string", [], {}]}))
        assert validator.validate(instance="a string")

    def test_const_false(self):
        validator = Enum(schema=annotate({"enum": [12434]}))
        assert not validator.validate(instance="astring")
