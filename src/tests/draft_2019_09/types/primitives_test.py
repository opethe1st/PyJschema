
import unittest

from jschema.draft_2019_09 import validate_once


class TestEnum(unittest.TestCase):
    def test_instance_in_enum(self):
        ok = validate_once(
            schema={"$id": "https://example.com/ope", "enum": ["Abc", 1224]},
            instance="Abc",
        ).ok
        self.assertTrue(ok)

    def test_instance_not_in_enum(self):
        ok = validate_once(
            schema={"$id": "https://example.com/ope", "enum": ["Abc", 1244]},
            instance=123,
        ).ok
        self.assertFalse(ok)


class TestConst(unittest.TestCase):
    def test_instance_equal_const(self):
        ok = validate_once(
            schema={"$id": "https://example.com/ope", "const": "ABC"}, instance="ABC"
        ).ok
        self.assertTrue(ok)

    def test_instance_not_equal_const(self):
        ok = validate_once(
            schema={"$id": "https://example.com/ope", "const": "DEF"}, instance=123
        ).ok
        self.assertFalse(ok)


class TestNull(unittest.TestCase):
    def test_instance_null(self):
        ok = validate_once(
            schema={"$id": "https://example.com/ope", "type": "null"}, instance=None
        ).ok
        self.assertTrue(ok)

    def test_instance_not_null(self):
        ok = validate_once(
            schema={"$id": "https://example.com/ope", "type": "null"}, instance=123
        ).ok
        self.assertFalse(ok)
