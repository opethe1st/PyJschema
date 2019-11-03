import unittest

import parameterized

from jsonschema.draft_2019_09 import validate_once, build_validator
from jsonschema.common import attach_base_URIs


class TestEnum(unittest.TestCase):
    def test_instance_in_enum(self):
        ok = validate_once(schema={"$id": "https://example.com/ope", "enum": ["Abc", 1224, ]}, instance="Abc",).ok
        self.assertTrue(ok)

    def test_instance_not_in_enum(self):
        ok = validate_once(schema={"$id": "https://example.com/ope", "enum": ["Abc", 1244]}, instance=123,).ok
        self.assertFalse(ok)


class TestConst(unittest.TestCase):
    def test_instance_equal_const(self):
        ok = validate_once(schema={"$id": "https://example.com/ope", "const": "ABC"}, instance="ABC",).ok
        self.assertTrue(ok)

    def test_instance_not_equal_const(self):
        ok = validate_once(schema={"$id": "https://example.com/ope", "const": "DEF"}, instance=123,).ok
        self.assertFalse(ok)


class TestNull(unittest.TestCase):
    def test_instance_null(self):
        ok = validate_once(
            schema={
                "$id": "https://example.com/ope",
                "type": "null"
            },
            instance=None,
        ).ok
        self.assertTrue(ok)

    def test_instance_not_null(self):
        ok = validate_once(schema={"$id": "https://example.com/ope", "type": "null"}, instance=123,).ok
        self.assertFalse(ok)


class TestString(unittest.TestCase):

    @parameterized.parameterized.expand(
        [
            ('is a string', {"$id": "https://example.com/ope", 'type': "string"}, "abc"),
            ('pattern', {"$id": "https://example.com/ope", 'type': "string", "pattern": "abc"}, "abcmatch"),
            ('all keywords', {"$id": "https://example.com/ope", 'type': "string", "pattern": "abc", "minLength": 1, "maxLength": 10}, "abcmatch"),
        ]
    )
    def test_true(self, name, schema, instance):
        self.assertTrue(validate_once(schema=schema, instance=instance).ok)

    @parameterized.parameterized.expand(
        [
            ('not a string', {"$id": "https://example.com/ope", 'type': "string"}, 123),
            ("mininum", {"$id": "https://example.com/ope", 'type': "string", "minLength": 100}, "tooshort"),
            ("maximum", {"$id": "https://example.com/ope", 'type': "string", "maxLength": 1}, "toolong"),
            ("pattern", {"$id": "https://example.com/ope", 'type': "string", "pattern": "abc"}, "123match"),
        ]
    )
    def test_false(self, name, schema, instance):
        self.assertFalse(validate_once(schema=schema, instance=instance).ok)


class TestBoolean(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            ("true", {"$id": "https://example.com/ope", "type": "boolean"}, True),
            ("boolean", {"$id": "https://example.com/ope", "type": "boolean"}, False),
        ]

    )
    def test_instance_true(self, name, schema, instance):
        self.assertTrue(validate_once(schema=schema, instance=instance).ok)

    def test_instance_not_boolean(self):
        ok = validate_once(schema={"$id": "https://example.com/ope", "type": "boolean"}, instance=123,).ok
        self.assertFalse(ok)


class TestNumber(unittest.TestCase):

    @parameterized.parameterized.expand(
        [
            ("is number", {"$id": "https://example.com/ope", "type": "number"}, 123),
            ("multipleOf", {"$id": "https://example.com/ope", "type": "number", "multipleOf": 3}, 123),
            ("minimum", {"$id": "https://example.com/ope", "type": "number", "minimum": 3}, 3),
            ("exclusiveMinimum", {"$id": "https://example.com/ope", "type": "number", "exclusiveMinimum": 3}, 4),
            ("maximum", {"$id": "https://example.com/ope", "type": "number", "maximum": 3}, 3),
            ("exclusiveMaximum", {"$id": "https://example.com/ope", "type": "number", "exclusiveMaximum": 5}, 4),
            ("integer", {"$id": "https://example.com/ope", "type": "integer"}, 4),
        ]

    )
    def test_true(self, name, schema, instance):
        self.assertTrue(validate_once(schema=schema, instance=instance).ok)

    @parameterized.parameterized.expand(
        [
            ("is not number", {"$id": "https://example.com/ope", "type": "number"}, '123'),
            ("multipleOf", {"$id": "https://example.com/ope", "type": "number", "multipleOf": 4}, 123),
            ("minimum", {"$id": "https://example.com/ope", "type": "number", "minimum": 124}, 123),
            ("exclusiveMinimum", {"$id": "https://example.com/ope", "type": "number", "exclusiveMinimum": 124}, 124),
            ("maximum", {"$id": "https://example.com/ope", "type": "number", "maximum": 123}, 124),
            ("exclusiveMaximum", {"$id": "https://example.com/ope", "type": "number", "exclusiveMaximum": 124}, 124),
            ("integer", {"$id": "https://example.com/ope", "type": "integer"}, 124.012),
        ]

    )
    def test_false(self, name, schema, instance):
        self.assertFalse(validate_once(schema=schema, instance=instance).ok)


class TestArrayValidation(unittest.TestCase):

    @parameterized.parameterized.expand(
        [
            ('items', {"$id": "https://example.com/ope", "type": "array", "items": {"type": "string"}}, ['blah', 'balh2']),
            ('nested array', {"$id": "https://example.com/ope", "type": "array", "items": {"type": "array", "items": {"type": "string"}}}, [["s1", "s2"]]),
            ('items array', {"$id": "https://example.com/ope", "type": "array", "items": [{"type": "string"}]}, ["s1", "s2", 123]),
            ('items array', {"$id": "https://example.com/ope", "type": "array", "items": [{"type": "string"}, {"type": "string"}]}, ["s1"]),
            (
                'items array with different types',
                {"$id": "https://example.com/ope", "type": "array", "items": [{"type": "string"}, {"type": "string"}, {"type": "number"}]},
                ["s1", "s2", 123]
            ),
            (
                'items array with additionalItems',
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "items": [{"type": "string"}],
                    "additionalItems": {"type": "number"}
                },
                ["s1", 123, 123]
            ),
            ('minItems', {"$id": "https://example.com/ope", "type": "array", "minItems": 1}, ["blah"]),
            ('maxItems', {"$id": "https://example.com/ope", "type": "array", "maxItems": 1}, ["blah"]),
            ('uniqueItems true', {"$id": "https://example.com/ope", "type": "array", "uniqueItems": True}, ["bakh", "blahs"]),
            ('uniqueItems true with empty array', {"$id": "https://example.com/ope", "type": "array", "uniqueItems": True}, []),
            ('uniqueItems false', {"$id": "https://example.com/ope", "type": "array", "uniqueItems": False}, ["aa", "aa"]),
            (
                'contains',
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "contains": {"type": "string"},
                },
                [123, 124, "aa"]
            ),
            (
                'contains with maxContains',
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "contains": {"type": "string"},
                    "maxContains": 1,
                },
                [123, 124, "aa"]
            ),
            (
                'minContains and maxContains has no effect without contains',
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "minContains": 1,
                    "maxContains": 1,
                },
                [123, 124, "aa"]
            ),
        ]
    )
    def test_true(self, name, schema, instance):
        res = validate_once(schema=schema, instance=instance)
        self.assertTrue(res.ok)

    @parameterized.parameterized.expand(
        [
            ('is list', {"$id": "https://example.com/ope", "type": "array"}, "not an array"),
            ('items', {"$id": "https://example.com/ope", "type": "array", "items": {"type": "string"}}, ['blah', 123]),
            ('items', {"$id": "https://example.com/ope", "type": "array", "items": [{"type": "string"}]}, [123]),
            ('minItems', {"$id": "https://example.com/ope", "type": "array", "minItems": 1}, []),
            ('maxItems', {"$id": "https://example.com/ope", "type": "array", "maxItems": 1}, ["balh", "blah2"]),
            (
                'items array with additionalItems',
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "items": [{"type": "string"}],
                    "additionalItems": {"type": "number"}
                },
                ["s1", '123', 123]
            ),
            ('uniqueItems with arrays since arrays are not hashable', {"$id": "https://example.com/ope", "type": "array", "uniqueItems": True}, [["k1", "v1"], ["k1", "v1"]]),
            ('uniqueItems with objects since objects are not hashable', {"$id": "https://example.com/ope", "type": "array", "uniqueItems": True}, [{"k1": "v1"}, {"k1": "v1"}]),
            ('contains', {"$id": "https://example.com/ope", "type": "array", "contains": {"type": "string"}}, [123, 124, 1234]),
            ('the number of items match contains is more than maxContains', {"$id": "https://example.com/ope", "type": "array", "contains": {"type": "string"}, "maxContains": 2}, ["123", "124", "1234"]),
        ]
    )
    def test_false(self, name, schema, instance):
        self.assertFalse(validate_once(schema=schema, instance=instance).ok)


class TestObject(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            ('is object', {"$id": "https://example.com/ope", "type": "object"}, {"k1": "v1"}),
            (
                'object with properties',
                {
                    "$id": "https://example.com/ope",
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
                    "$id": "https://example.com/ope",
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
                    "$id": "https://example.com/ope",
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
                    "$id": "https://example.com/ope",
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
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "minProperties": 1
                },
                {"abcde": "ab", "abc": "abcdefghij"},
            ),
            (
                'maxProperties',
                {
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "maxProperties": 5
                },
                {"abcde": "ab", "abc": "abcdefghij"},
            ),
            (
                'patternProperties',
                {
                    "$id": "https://example.com/ope",
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
                    "$id": "https://example.com/ope",
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
            ('is object', {"$id": "https://example.com/ope", "type": "object"}, "not an object"),
            ('object with non-string keys', {"$id": "https://example.com/ope", "type": "object"}, {123: "value"}),
            (
                'object with properties',
                {
                    "$id": "https://example.com/ope",
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
                    "$id": "https://example.com/ope",
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
                    "$id": "https://example.com/ope",
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
                    "$id": "https://example.com/ope",
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
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "minProperties": 4
                },
                {"abcde": "ab", "abc": "abcdefghij"},
            ),
            (
                'maxProperties',
                {
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "maxProperties": 1
                },
                {"abcde": "ab", "abc": "abcdefghij"},
            ),
            (
                'patternProperties',
                {
                    "$id": "https://example.com/ope",
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
                    "$id": "https://example.com/ope",
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
            ("random int", {"$id": "https://example.com/ope",}, 1234),
            ("random string", {"$id": "https://example.com/ope",}, "1234"),
            ("null", {"$id": "https://example.com/ope",}, None),
            ("false", {"$id": "https://example.com/ope",}, False),
            ("array with different stuff", {"$id": "https://example.com/ope",}, [False, 1, "1224"]),
            ("object with different stuff", {"$id": "https://example.com/ope",}, {"k1": 123, "k2": "v1"}),
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
                    "$id": "https://example.com/ope",
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
                    "$id": "https://example.com/ope",
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
        ('number', {"$id": "https://example.com/ope", "type": ["string", "number"]}, 123),
        ('string', {"$id": "https://example.com/ope", "type": ["string", "number"]}, "sdbfgs"),
        ('number with maximum keyword', {"$id": "https://example.com/ope", "type": ["string", "number"], "maximum": 200}, 123),
        ('string with maximum keyword', {"$id": "https://example.com/ope", "type": ["string", "number"], "maxLength": 10}, "sdbfgs"),
    ])
    def test_true(self, name, schema, instance):
        res = validate_once(schema, instance)
        self.assertTrue(res.ok)


    @parameterized.parameterized.expand([
        ('array not accepted by string and number', {"$id": "https://example.com/ope", "type": ["string", "number"]}, [123]),
        ('dict not accepted string and number', {"$id": "https://example.com/ope", "type": ["string", "number"]}, {"k": "v"}),
        ('number fails validation', {"$id": "https://example.com/ope", "type": ["string", "number"], "maximum": 5}, 10),
        ('string fails validation', {"$id": "https://example.com/ope", "type": ["string", "number"], "maxLength": 3}, "abcdefghi"),
    ])
    def test_false(self, name, schema, instance):
        res = validate_once(schema, instance)
        self.assertFalse(res.ok)


class TestCanonicalId(unittest.TestCase):
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
    def test_true(self, name, schema, instance):
        res = validate_once(schema, instance)
        self.assertTrue(res.ok)


class TestBooleanLogic(unittest.TestCase):
    @parameterized.parameterized.expand([
        (
            'if condition true',
            {
                "$id": "mysite",
                "if": {
                    "type": "string",
                },
                "then": {
                    "type": "string",
                    "maxLength": 40
                },
                "else": {
                    "type": "number",
                    "maximum": 5
                }
            },
            "some string"
        ),
        (
            'if condition false',
            {
                "$id": "mysite",
                "if": {
                    "type": "string",
                },
                "then": {
                    "type": "string",
                    "maxLength": 40
                },
                "else": {
                    "type": "number",
                    "maximum": 5
                }
            },
            4
        ),
    ])
    def test_true(self, name, schema, instance):
        res = validate_once(schema, instance)
        self.assertTrue(res.ok)

    @parameterized.parameterized.expand([
        (
            'if condition true',
            {
                "$id": "mysite",
                "if": {
                    "type": "string",
                },
                "then": {
                    "type": "string",
                    "maxLength": 4
                },
                "else": {
                    "type": "number",
                    "maximum": 5
                }
            },
            "string too long"
        ),
        (
            'if condition false',
            {
                "$id": "mysite",
                "if": {
                    "type": "string",
                },
                "then": {
                    "type": "string",
                    "maxLength": 4
                },
                "else": {
                    "type": "number",
                    "maximum": 5
                }
            },
            100
        ),
    ])
    def test_false(self, name, schema, instance):
        res = validate_once(schema, instance)
        self.assertFalse(res.ok)
