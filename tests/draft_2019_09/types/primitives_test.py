import unittest

from pyjschema.draft_2019_09 import validate


class TestEnum(unittest.TestCase):
    def test_instance_in_enum(self):
        res = validate(
            schema={"$id": "https://example.com/ope", "enum": ["Abc", 1224]},
            instance="Abc",
        )
        self.assertTrue(res)

    def test_instance_not_in_enum(self):
        res = validate(
            schema={"$id": "https://example.com/ope", "enum": ["Abc", 1244]},
            instance=123,
        )
        self.assertFalse(res)


class TestConst(unittest.TestCase):
    def test_instance_equal_const(self):
        res = validate(
            schema={"$id": "https://example.com/ope", "const": "ABC"}, instance="ABC"
        )
        self.assertTrue(res)

    def test_instance_not_equal_const(self):
        res = validate(
            schema={"$id": "https://example.com/ope", "const": "DEF"}, instance=123
        )
        self.assertFalse(res)


class TestNull(unittest.TestCase):
    def test_instance_null(self):
        res = validate(
            schema={"$id": "https://example.com/ope", "type": "null"}, instance=None
        )
        self.assertTrue(res)

    def test_instance_not_null(self):
        res = validate(
            schema={"$id": "https://example.com/ope", "type": "null"}, instance=123
        )
        self.assertFalse(res)
