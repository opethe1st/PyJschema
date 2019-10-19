import unittest

import parameterized

from jsonschema.draft_2019_09 import validate_once, build_validator
from jsonschema.common import attach_base_URIs


class TestEnum(unittest.TestCase):
    def test_instance_in_enum(self):
        ok = validate_once(schema={"enum": ["Abc", 1224, ]}, instance="Abc",).ok
        self.assertTrue(ok)

    def test_instance_not_in_enum(self):
        ok = validate_once(schema={"enum": ["Abc", 1244]}, instance=123,).ok
        self.assertFalse(ok)


class TestConst(unittest.TestCase):
    def test_instance_equal_const(self):
        ok = validate_once(schema={"const": "ABC"}, instance="ABC",).ok
        self.assertTrue(ok)

    def test_instance_not_equal_const(self):
        ok = validate_once(schema={"const": "DEF"}, instance=123,).ok
        self.assertFalse(ok)


class TestNull(unittest.TestCase):
    def test_instance_null(self):
        ok = validate_once(
            schema={
                "type": "null"
            },
            instance=None,
        ).ok
        self.assertTrue(ok)

    def test_instance_not_null(self):
        ok = validate_once(schema={"type": "null"}, instance=123,).ok
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
        self.assertTrue(validate_once(schema=schema, instance=instance).ok)

    @parameterized.parameterized.expand(
        [
            ('not a string', {'type': "string"}, 123),
            ("mininum", {'type': "string", "minLength": 100}, "tooshort"),
            ("maximum", {'type': "string", "maxLength": 1}, "toolong"),
            ("pattern", {'type': "string", "pattern": "abc"}, "123match"),
        ]
    )
    def test_false(self, name, schema, instance):
        self.assertFalse(validate_once(schema=schema, instance=instance).ok)


class TestBoolean(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            ("true", {"type": "boolean"}, True),
            ("boolean", {"type": "boolean"}, False),
        ]

    )
    def test_instance_true(self, name, schema, instance):
        self.assertTrue(validate_once(schema=schema, instance=instance).ok)

    def test_instance_not_boolean(self):
        ok = validate_once(schema={"type": "boolean"}, instance=123,).ok
        self.assertFalse(ok)


class TestNumber(unittest.TestCase):

    @parameterized.parameterized.expand(
        [
            ("is number", {"type": "number"}, 123),
            ("multipleOf", {"type": "number", "multipleOf": 3}, 123),
            ("minimum", {"type": "number", "minimum": 3}, 3),
            ("exclusiveMinimum", {"type": "number", "exclusiveMinimum": 3}, 4),
            ("maximum", {"type": "number", "maximum": 3}, 3),
            ("exclusiveMaximum", {"type": "number", "exclusiveMaximum": 5}, 4),
            ("integer", {"type": "integer"}, 4),
        ]

    )
    def test_true(self, name, schema, instance):
        self.assertTrue(validate_once(schema=schema, instance=instance).ok)

    @parameterized.parameterized.expand(
        [
            ("is not number", {"type": "number"}, '123'),
            ("multipleOf", {"type": "number", "multipleOf": 4}, 123),
            ("minimum", {"type": "number", "minimum": 124}, 123),
            ("exclusiveMinimum", {"type": "number", "exclusiveMinimum": 124}, 124),
            ("maximum", {"type": "number", "maximum": 123}, 124),
            ("exclusiveMaximum", {"type": "number", "exclusiveMaximum": 124}, 124),
            ("integer", {"type": "integer"}, 124.012),
        ]

    )
    def test_false(self, name, schema, instance):
        self.assertFalse(validate_once(schema=schema, instance=instance).ok)


class TestArrayValidation(unittest.TestCase):

    @parameterized.parameterized.expand(
        [
            ('items', {"type": "array", "items": {"type": "string"}}, ['blah', 'balh2']),
            ('nested array', {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}, [["s1", "s2"]]),
            ('items array', {"type": "array", "items": [{"type": "string"}]}, ["s1", "s2", 123]),
            ('items array', {"type": "array", "items": [{"type": "string"}, {"type": "string"}]}, ["s1"]),
            (
                'items array with different types',
                {"type": "array", "items": [{"type": "string"}, {"type": "string"}, {"type": "number"}]},
                ["s1", "s2", 123]
            ),
            (
                'items array with additionalItems',
                {
                    "type": "array",
                    "items": [{"type": "string"}],
                    "additionalItems": {"type": "number"}
                },
                ["s1", 123, 123]
            ),
            ('minItems', {"type": "array", "minItems": 1}, ["blah"]),
            ('maxItems', {"type": "array", "maxItems": 1}, ["blah"]),
            ('uniqueItems true', {"type": "array", "uniqueItems": True}, ["bakh", "blahs"]),
            ('uniqueItems true with empty array', {"type": "array", "uniqueItems": True}, []),
            ('uniqueItems false', {"type": "array", "uniqueItems": False}, ["aa", "aa"]),
            ('contains', {"type": "array", "contains": {"type": "string"}}, [123, 124, "aa"]),
        ]
    )
    def test_true(self, name, schema, instance):
        self.assertTrue(validate_once(schema=schema, instance=instance).ok)

    @parameterized.parameterized.expand(
        [
            ('is list', {"type": "array"}, "not an array"),
            ('items', {"type": "array", "items": {"type": "string"}}, ['blah', 123]),
            ('items', {"type": "array", "items": [{"type": "string"}]}, [123]),
            ('minItems', {"type": "array", "minItems": 1}, []),
            ('maxItems', {"type": "array", "maxItems": 1}, ["balh", "blah2"]),
            (
                'items array with additionalItems',
                {
                    "type": "array",
                    "items": [{"type": "string"}],
                    "additionalItems": {"type": "number"}
                },
                ["s1", '123', 123]
            ),
            ('uniqueItems with arrays since arrays are not hashable', {"type": "array", "uniqueItems": True}, [["k1", "v1"], ["k1", "v1"]]),
            ('uniqueItems with objects since objects are not hashable', {"type": "array", "uniqueItems": True}, [{"k1": "v1"}, {"k1": "v1"}]),
            ('contains', {"type": "array", "contains": {"type": "string"}}, [123, 124, 1234]),
        ]
    )
    def test_false(self, name, schema, instance):
        self.assertFalse(validate_once(schema=schema, instance=instance).ok)


class TestObject(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            ('is object', {"type": "object"}, {"k1": "v1"}),
            (
                'object with properties',
                {
                    "type": "object",
                    "properties": {
                        "shortname": {"type": "string", "maxLength": 3},
                        "longname": {"type": "string", "maxLength": 15},
                    }
                },
                {"shortname": "ab", "longname": "abcdefghij"},
            ),
            (
                'additionalProperties',
                {
                    "type": "object",
                    "properties": {
                        "shortname": {"type": "string", "maxLength": 3},
                        "longname": {"type": "string", "maxLength": 15},
                    },
                    "additionalProperties": {
                        "type": "number"
                    }
                },
                {"shortname": "ab", "longname": "abcdefghij", "score": 1234}
            ),
            (
                'object with required',
                {
                    "type": "object",
                    "required": [
                        "shortname",
                        "longname",
                    ]
                },
                {"shortname": "ab", "longname": "abcdefghij"},
            ),
            (
                'object with propertyNames',
                {
                    "type": "object",
                    "propertyNames": {
                        "pattern": "[a-z]*"
                    }
                },
                {"": "ab", "abc": "abcdefghij"},
            ),
            (
                'minProperties',
                {
                    "type": "object",
                    "minProperties": 1
                },
                {"abcde": "ab", "abc": "abcdefghij"},
            ),
            (
                'maxProperties',
                {
                    "type": "object",
                    "maxProperties": 5
                },
                {"abcde": "ab", "abc": "abcdefghij"},
            ),
            (
                'patternProperties',
                {
                    "type": "object",
                    "patternProperties": {
                        "^S_": {"type": "string"},
                        "^I_": {"type": "integer"}
                    },
                    "additionalProperties": False
                },
                {"S_25": "This is a string", "I_0": 42}
            ),
            (
                'additionalProperties false with empty object',
                {
                    "type": "object",
                    "additionalProperties": False
                },
                {}
            ),
        ]
    )
    def test_true(self, name, schema, instance):
        self.assertTrue(validate_once(schema=schema, instance=instance).ok)

    @parameterized.parameterized.expand(
        [
            ('is object', {"type": "object"}, "not an object"),
            ('object with non-string keys', {"type": "object"}, {123: "value"}),
            (
                'object with properties',
                {
                    "type": "object",
                    "properties": {
                        "shortname": {"type": "string", "maxLength": 3},
                        "longname": {"type": "string", "maxLength": 4},
                    }
                },
                {"shortname": "ab", "longname": "abcdefghij", "fullname": "short long"}
            ),
            (
                'additionalProperties',
                {
                    "type": "object",
                    "properties": {
                        "shortname": {"type": "string", "maxLength": 3},
                        "longname": {"type": "string", "maxLength": 15},
                    },
                    "additionalProperties": {
                        "type": "number"
                    }
                },
                {"shortname": "ab", "longname": "abcdefghij", "score": "this is clearly not a score"}
            ),
            (
                'object with required',
                {
                    "type": "object",
                    "required": [
                        "shortname",
                        "longname",
                        "firstname",
                    ]
                },
                {"shortname": "ab", "longname": "abcdefghij"},
            ),
            (
                'object with propertyNames',
                {
                    "type": "object",
                    "propertyNames": {
                        "pattern": "[a-z]+"
                    }
                },
                {"": "ab", "abc": "abcdefghij", "123": "doesnt conform to pattern"},
            ),
            (
                'minProperties',
                {
                    "type": "object",
                    "minProperties": 4
                },
                {"abcde": "ab", "abc": "abcdefghij"},
            ),
            (
                'maxProperties',
                {
                    "type": "object",
                    "maxProperties": 1
                },
                {"abcde": "ab", "abc": "abcdefghij"},
            ),
            (
                'patternProperties',
                {
                    "type": "object",
                    "patternProperties": {
                        "^S_": {"type": "string"},
                        "^I_": {"type": "integer"}
                    },
                    "additionalProperties": False
                },
                {"S_0": 42}
            ),
            (
                'just AdditionalProperties false',
                {
                    "type": "object",
                    "additionalProperties": False
                },
                {"key": "no properties allowed"}
            ),
        ]
    )
    def test_false(self, name, schema, instance):
        self.assertFalse(validate_once(schema=schema, instance=instance).ok)


class TestTrue(unittest.TestCase):

    @parameterized.parameterized.expand(
        [
            ("random int", True, 1234),
            ("random string", True, "1234"),
            ("null", True, None),
            ("false", True, False),
            ("array with different stuff", True, [False, 1, "1224"]),
            ("object with different stuff", True, {"k1": 123, "k2": "v1"}),
        ]
    )
    def test_true(self, name, schema, instance):
        self.assertTrue(validate_once(schema=schema, instance=instance).ok)

    @parameterized.parameterized.expand(
        [
            ("random int", {}, 1234),
            ("random string", {}, "1234"),
            ("null", {}, None),
            ("false", {}, False),
            ("array with different stuff", {}, [False, 1, "1224"]),
            ("object with different stuff", {}, {"k1": 123, "k2": "v1"}),
        ]
    )
    def test_empty_schema(self, name, schema, instance):
        self.assertTrue(validate_once(schema=schema, instance=instance).ok)


class TestFalse(unittest.TestCase):

    @parameterized.parameterized.expand(
        [
            ("random int", False, 1234),
            ("random string", False, "1234"),
            ("null", False, None),
            ("false", False, False),
            ("array with different stuff", False, [False, 1, "1224"]),
            ("object with different stuff", False, {"k1": 123, "k2": "v1"}),
        ]
    )
    def test_true(self, name, schema, instance):
        self.assertFalse(validate_once(schema=schema, instance=instance).ok)


class TestValidatorWithRef(unittest.TestCase):

    @parameterized.parameterized.expand(
        [
            (
                "testing testing",
                {
                    "type": "object",
                    "$id": "www.myschema.com/test",
                    "properties": {
                        "name": {
                            "$anchor": "string_property",
                            "type": "string"
                        },
                        "surname": {
                            "$ref": "www.myschema.com/test#string_property"
                        }
                    }
                },
                {
                    "name": "abcd",
                    "surname": "abcd",
                }
            ),
        ]
    )
    def test_true(self, name, schema, instance):
        res = validate_once(schema, instance)
        self.assertTrue(res.ok)

    @parameterized.parameterized.expand(
        [
            (
                "testing testing",
                {
                    "type": "object",
                    "$id": "www.myschema.com/test",
                    "properties": {
                        "name": {
                            "$anchor": "string_property",
                            "type": "string"
                        },
                        "surname": {
                            "$ref": "www.myschema.com/test#string_property"
                        }
                    }
                },
                {
                    "name": "abcd",
                    "surname": 123,
                }
            ),
        ]
    )
    def test_false(self, name, schema, instance):
        res = validate_once(schema, instance)
        self.assertFalse(res.ok)


class TestTypes(unittest.TestCase):
    @parameterized.parameterized.expand([
        ('number', {"type": ["string", "number"]}, 123),
        ('string', {"type": ["string", "number"]}, "sdbfgs"),
        ('number with maximum keyword', {"type": ["string", "number"], "maximum": 200}, 123),
        ('string with maximum keyword', {"type": ["string", "number"], "maxLength": 10}, "sdbfgs"),
    ])
    def test_true(self, name, schema, instance):
        res = validate_once(schema, instance)
        self.assertTrue(res.ok)


    @parameterized.parameterized.expand([
        ('array not accepted by string and number', {"type": ["string", "number"]}, [123]),
        ('dict not accepted string and number', {"type": ["string", "number"]}, {"k": "v"}),
        ('number fails validation', {"type": ["string", "number"], "maximum": 5}, 10),
        ('string fails validation', {"type": ["string", "number"], "maxLength": 3}, "abcdefghi"),
    ])
    def test_false(self, name, schema, instance):
        res = validate_once(schema, instance)
        self.assertFalse(res.ok)


class TestId(unittest.TestCase):
    @parameterized.parameterized.expand([
        (
            'number',
            {
                "$id": "mysite.org/array",
                "type": "object",
                "properties": {
                    "name": {
                        "$id": "mysite.org/name",
                        "$anchor": "blah",
                        "type": "string",
                    },
                    "surname": {
                        "$ref": "mysite.org/name"
                    },
                    "firstname": {
                        "$ref": "mysite.org/name"
                    },
                }

            },
            {"name": "abc", "surname": "def", "firstname": "312"}
        ),
    ])
    def test_xxx(self, name, schema, instance):
        res = validate_once(schema, instance)
        self.assertTrue(res.ok)
