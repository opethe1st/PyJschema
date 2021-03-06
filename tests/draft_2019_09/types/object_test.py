import unittest

import parameterized

from pyjschema.draft_2019_09 import validate


class TestObject(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            (
                "is object",
                {"$id": "https://example.com/ope", "type": "object"},
                {"k1": "v1"},
            ),
            (
                "object with properties",
                {
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "properties": {
                        "shortname": {"type": "string", "maxLength": 3},
                        "longname": {"type": "string", "maxLength": 15},
                    },
                },
                {"shortname": "ab", "longname": "abcdefghij"},
            ),
            (
                "additionalProperties",
                {
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "properties": {
                        "shortname": {"type": "string", "maxLength": 3},
                        "longname": {"type": "string", "maxLength": 15},
                    },
                    "additionalProperties": {"type": "number"},
                },
                {"shortname": "ab", "longname": "abcdefghij", "score": 1234},
            ),
            (
                "object with required",
                {
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "required": ["shortname", "longname"],
                },
                {"shortname": "ab", "longname": "abcdefghij"},
            ),
            (
                "object with propertyNames",
                {
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "propertyNames": {"pattern": "[a-z]*"},
                },
                {"": "ab", "abc": "abcdefghij"},
            ),
            (
                "minProperties",
                {
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "minProperties": 1,
                },
                {"abcde": "ab", "abc": "abcdefghij"},
            ),
            (
                "maxProperties",
                {
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "maxProperties": 5,
                },
                {"abcde": "ab", "abc": "abcdefghij"},
            ),
            (
                "patternProperties",
                {
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "patternProperties": {
                        "^S_": {"type": "string"},
                        "^I_": {"type": "integer"},
                    },
                    "additionalProperties": False,
                },
                {"S_25": "This is a string", "I_0": 42},
            ),
            (
                "additionalProperties false with empty object",
                {
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "additionalProperties": False,
                },
                {},
            ),
            (
                "dependentRequired object empty",
                {
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "dependentRequired": {"firstname": ["lastname"]},
                },
                {},
            ),
            (
                "dependentRequired object ",
                {
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "dependentRequired": {"firstname": ["lastname"]},
                },
                {"firstname": "Ope", "lastname": "Ope"},
            ),
        ]
    )
    def test_true(self, name, schema, instance):
        self.assertTrue(validate(schema=schema, instance=instance))

    @parameterized.parameterized.expand(
        [
            (
                "is object",
                {"$id": "https://example.com/ope", "type": "object"},
                "not an object",
            ),
            (
                "object with properties",
                {
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "properties": {
                        "shortname": {"type": "string", "maxLength": 3},
                        "longname": {"type": "string", "maxLength": 4},
                    },
                },
                {"shortname": "ab", "longname": "abcdefghij", "fullname": "short long"},
            ),
            (
                "additionalProperties",
                {
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "properties": {
                        "shortname": {"type": "string", "maxLength": 3},
                        "longname": {"type": "string", "maxLength": 15},
                    },
                    "additionalProperties": {"type": "number"},
                },
                {
                    "shortname": "ab",
                    "longname": "abcdefghij",
                    "score": "this is clearly not a score",
                },
            ),
            (
                "object with required",
                {
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "required": ["shortname", "longname", "firstname"],
                },
                {"shortname": "ab", "longname": "abcdefghij"},
            ),
            (
                "object with propertyNames",
                {
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "propertyNames": {"pattern": "[a-z]+"},
                },
                {"": "ab", "abc": "abcdefghij", "123": "doesnt conform to pattern"},
            ),
            (
                "minProperties",
                {
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "minProperties": 4,
                },
                {"abcde": "ab", "abc": "abcdefghij"},
            ),
            (
                "maxProperties",
                {
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "maxProperties": 1,
                },
                {"abcde": "ab", "abc": "abcdefghij"},
            ),
            (
                "patternProperties",
                {
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "patternProperties": {
                        "^S_": {"type": "string"},
                        "^I_": {"type": "integer"},
                    },
                    "additionalProperties": False,
                },
                {"S_0": 42},
            ),
            (
                "just AdditionalProperties false",
                {
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "additionalProperties": False,
                },
                {"key": "no properties allowed"},
            ),
            (
                "dependentRequired object ",
                {
                    "$id": "https://example.com/ope",
                    "type": "object",
                    "dependentRequired": {"firstname": ["lastname"]},
                },
                {"firstname": "Ope"},
            ),
        ]
    )
    def test_false(self, name, schema, instance):
        self.assertFalse(validate(schema=schema, instance=instance))
