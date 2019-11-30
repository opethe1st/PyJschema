import unittest

import parameterized

from jschema.draft_2019_09 import validate_once

# TODO: Ope do these tests make sense


class TestValidatorWithRef(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            (
                "testing testing",
                {
                    "type": "object",
                    "$id": "https://www.myschema.com/test",
                    "properties": {
                        "name": {"$anchor": "string_property", "type": "string"},
                        "surname": {
                            "$ref": "https://www.myschema.com/test#string_property"
                        },
                    },
                },
                {"name": "abcd", "surname": "abcd"},
            )
        ]
    )
    def test_true(self, name, schema, instance):
        res = validate_once(schema, instance)
        self.assertTrue(res)

    @parameterized.parameterized.expand(
        [
            (
                "testing testing",
                {
                    "type": "object",
                    "$id": "https://www.myschema.com/test",
                    "properties": {
                        "name": {"$anchor": "string_property", "type": "string"},
                        "surname": {
                            "$ref": "https://www.myschema.com/test#string_property"
                        },
                    },
                },
                {"name": "abcd", "surname": 123},
            )
        ]
    )
    def test_false(self, name, schema, instance):
        res = validate_once(schema, instance)
        self.assertFalse(res)


class TestTypes(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            (
                "number",
                {"$id": "https://example.com/ope", "type": ["string", "number"]},
                123,
            ),
            (
                "string",
                {"$id": "https://example.com/ope", "type": ["string", "number"]},
                "sdbfgs",
            ),
            (
                "number with maximum keyword",
                {
                    "$id": "https://example.com/ope",
                    "type": ["string", "number"],
                    "maximum": 200,
                },
                123,
            ),
            (
                "string with maximum keyword",
                {
                    "$id": "https://example.com/ope",
                    "type": ["string", "number"],
                    "maxLength": 10,
                },
                "sdbfgs",
            ),
        ]
    )
    def test_true(self, name, schema, instance):
        res = validate_once(schema, instance)
        self.assertTrue(res)

    @parameterized.parameterized.expand(
        [
            (
                "array not accepted by string and number",
                {"$id": "https://example.com/ope", "type": ["string", "number"]},
                [123],
            ),
            (
                "dict not accepted string and number",
                {"$id": "https://example.com/ope", "type": ["string", "number"]},
                {"k": "v"},
            ),
            (
                "number fails validation",
                {
                    "$id": "https://example.com/ope",
                    "type": ["string", "number"],
                    "maximum": 5,
                },
                10,
            ),
            (
                "string fails validation",
                {
                    "$id": "https://example.com/ope",
                    "type": ["string", "number"],
                    "maxLength": 3,
                },
                "abcdefghi",
            ),
        ]
    )
    def test_false(self, name, schema, instance):
        res = validate_once(schema, instance)
        self.assertFalse(res)


class TestCanonicalId(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            (
                "number",
                {
                    "$id": "https://mysite.org/array",
                    "type": "object",
                    "properties": {
                        "name": {
                            "$id": "https://mysite.org/name",
                            "$anchor": "blah",
                            "type": "string",
                        },
                        "surname": {"$ref": "https://mysite.org/name"},
                        "firstname": {"$ref": "https://mysite.org/name"},
                    },
                },
                {"name": "abc", "surname": "def", "firstname": "312"},
            )
        ]
    )
    def test_true(self, name, schema, instance):
        res = validate_once(schema, instance)
        self.assertTrue(res)


class TestKeywordValidationWithoutType(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            (
                "maxLength validation without the type keyword",
                {"$id": "mysite", "maxLength": 10},
                "a string",
            ),
            (
                "maxLength validation doesnt validate number",
                {"$id": "mysite", "maxLength": 10},
                34,
            ),
            ("maximum validation works", {"$id": "mysite", "maximum": 100}, 34),
        ]
    )
    def test_true(self, name, schema, instance):
        res = validate_once(schema, instance)
        self.assertTrue(res)
