import unittest

import parameterized
from jsonschema.draft_06.validator import build_validator


def validate(schema, instance) -> bool:
    return build_validator(schema=schema).validate(instance).ok


class TestEnum(unittest.TestCase):
    def test_instance_in_enum(self):
        ok = validate(schema={"enum": ["Abc", 1224, ]}, instance="Abc",)
        self.assertTrue(ok)

    def test_instance_not_in_enum(self):
        ok = validate(schema={"enum": ["Abc", 1244]}, instance=123,)
        self.assertFalse(ok)


class TestConst(unittest.TestCase):
    def test_instance_equal_const(self):
        ok = validate(schema={"const": "ABC"}, instance="ABC",)
        self.assertTrue(ok)

    def test_instance_not_equal_const(self):
        ok = validate(schema={"const": "DEF"}, instance=123,)
        self.assertFalse(ok)


class TestNull(unittest.TestCase):
    def test_instance_null(self):
        ok = validate(
            schema={
                "type": "null"
            },
            instance=None,
        )
        self.assertTrue(ok)

    def test_instance_not_null(self):
        ok = validate(schema={"type": "null"}, instance=123,)
        self.assertFalse(ok)


class TestString(unittest.TestCase):

    @parameterized.parameterized.expand(
        [
            ('is a string', {'type': "string"}, "abc"),
            ('pattern', {'type': "string", "pattern": "abc"}, "abcmatch"),
            ('all keywords', {'type': "string", "pattern": "abc", "minLength": 1, "maxLength": 10}, "abcmatch"),
        ]
    )
    def test_true(self, name, schema, instance):
        self.assertTrue(validate(schema=schema, instance=instance))

    @parameterized.parameterized.expand(
        [
            ('not a string', {'type': "string"}, 123),
            ("mininum", {'type': "string", "minLength": 100}, "tooshort"),
            ("maximum", {'type': "string", "maxLength": 1}, "toolong"),
            ("pattern", {'type': "string", "pattern": "abc"}, "123match"),
        ]
    )
    def test_false(self, name, schema, instance):
        self.assertFalse(validate(schema=schema, instance=instance))


class TestBoolean(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            ("true", {"type": "boolean"}, True),
            ("boolean", {"type": "boolean"}, False),
        ]

    )
    def test_instance_true(self, name, schema, instance):
        self.assertTrue(validate(schema=schema, instance=instance))

    def test_instance_not_boolean(self):
        ok = validate(schema={"type": "boolean"}, instance=123,)
        self.assertFalse(ok)


class TestNumber(unittest.TestCase):

    @parameterized.parameterized.expand(
        [
            ("is number", {"type": "number"}, 123),
            ("multipleOf", {"type": "number", "multipleOf": 3}, 123),
        ]

    )
    def test_true(self, name, schema, instance):
        self.assertTrue(validate(schema=schema, instance=instance))

    @parameterized.parameterized.expand(
        [
            ("is not number", {"type": "number"}, '123'),
            ("multipleOf", {"type": "number", "multipleOf": 4}, 123),
        ]

    )
    def test_false(self, name, schema, instance):
        self.assertFalse(validate(schema=schema, instance=instance))


class TestArrayValidation(unittest.TestCase):

    @parameterized.parameterized.expand(
        [
            ('items', {"type": "array", "items": {"type": "string"}}, ['blah', 'balh2']),
            ('nested array', {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}, [["s1", "s2"]]),
            ('items array', {"type": "array", "items": [{"type": "string"}]}, ["s1", "s2", 123]),
            (
                'items array with different types',
                {"type": "array", "items": [{"type": "string"}, {"type": "string"}, {"type": "number"}]},
                ["s1", "s2", 123]
            ),
            ('minItems', {"type": "array", "minItems": 1}, ["blah"]),
            ('maxItems', {"type": "array", "maxItems": 1}, ["blah"]),
            ('uniqueItems true', {"type": "array", "uniqueItems": True}, ["bakh", "blahs"]),
            ('uniqueItems true with empty array', {"type": "array", "uniqueItems": True}, []),
            ('uniqueItems false', {"type": "array", "uniqueItems": False}, ["aa", "aa"]),
        ]
    )
    def test_true(self, name, schema, instance):
        self.assertTrue(validate(schema=schema, instance=instance))

    @parameterized.parameterized.expand(
        [
            ('is list', {"type": "array"}, "not an array"),
            ('items', {"type": "array", "items": {"type": "string"}}, ['blah', 123]),
            ('minItems', {"type": "array", "minItems": 1}, []),
            ('maxItems', {"type": "array", "maxItems": 1}, ["balh", "blah2"]),
            ('uniqueItems with arrays since arrays are not hashable', {"type": "array", "uniqueItems": True}, [["k1", "v1"], ["k1", "v1"]]),
            ('uniqueItems with objects since objects are not hashable', {"type": "array", "uniqueItems": True}, [{"k1": "v1"}, {"k1": "v1"}]),
        ]
    )
    def test_false(self, name, schema, instance):
        self.assertFalse(validate(schema=schema, instance=instance))
