import unittest

import parameterized

from pyjschema.draft_2019_09 import validate_once


class TestArrayValidation(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            (
                "items",
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "items": {"type": "string"},
                },
                ["blah", "balh2"],
            ),
            (
                "nested array",
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "items": {"type": "array", "items": {"type": "string"}},
                },
                [["s1", "s2"]],
            ),
            (
                "items array",
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "items": [{"type": "string"}],
                },
                ["s1", "s2", 123],
            ),
            (
                "items array",
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "items": [{"type": "string"}, {"type": "string"}],
                },
                ["s1"],
            ),
            (
                "items array with different types",
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "items": [
                        {"type": "string"},
                        {"type": "string"},
                        {"type": "number"},
                    ],
                },
                ["s1", "s2", 123],
            ),
            (
                "items array with additionalItems",
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "items": [{"type": "string"}],
                    "additionalItems": {"type": "number"},
                },
                ["s1", 123, 123],
            ),
            (
                "minItems",
                {"$id": "https://example.com/ope", "type": "array", "minItems": 1},
                ["blah"],
            ),
            (
                "maxItems",
                {"$id": "https://example.com/ope", "type": "array", "maxItems": 1},
                ["blah"],
            ),
            (
                "uniqueItems true",
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "uniqueItems": True,
                },
                ["bakh", "blahs"],
            ),
            (
                "uniqueItems true with empty array",
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "uniqueItems": True,
                },
                [],
            ),
            (
                "uniqueItems false",
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "uniqueItems": False,
                },
                ["aa", "aa"],
            ),
            (
                "contains",
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "contains": {"type": "string"},
                },
                [123, 124, "aa"],
            ),
            (
                "contains with maxContains",
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "contains": {"type": "string"},
                    "maxContains": 1,
                },
                [123, 124, "aa"],
            ),
            (
                "minContains and maxContains has no effect without contains",
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "minContains": 1,
                    "maxContains": 1,
                },
                [123, 124, "aa"],
            ),
        ]
    )
    def test_true(self, name, schema, instance):
        res = validate_once(schema=schema, instance=instance)
        self.assertTrue(res)

    @parameterized.parameterized.expand(
        [
            (
                "is list",
                {"$id": "https://example.com/ope", "type": "array"},
                "not an array",
            ),
            (
                "items",
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "items": {"type": "string"},
                },
                ["blah", 123],
            ),
            (
                "items",
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "items": [{"type": "string"}],
                },
                [123],
            ),
            (
                "minItems",
                {"$id": "https://example.com/ope", "type": "array", "minItems": 1},
                [],
            ),
            (
                "maxItems",
                {"$id": "https://example.com/ope", "type": "array", "maxItems": 1},
                ["balh", "blah2"],
            ),
            (
                "items array with additionalItems",
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "items": [{"type": "string"}],
                    "additionalItems": {"type": "number"},
                },
                ["s1", "123", 123],
            ),
            (
                "uniqueItems with arrays since arrays are not hashable",
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "uniqueItems": True,
                },
                [["k1", "v1"], ["k1", "v1"]],
            ),
            (
                "uniqueItems with objects since objects are not hashable",
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "uniqueItems": True,
                },
                [{"k1": "v1"}, {"k1": "v1"}],
            ),
            (
                "contains",
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "contains": {"type": "string"},
                },
                [123, 124, 1234],
            ),
            (
                "the number of items match contains is more than maxContains",
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "contains": {"type": "string"},
                    "maxContains": 2,
                },
                ["123", "124", "1234"],
            ),
        ]
    )
    def test_false(self, name, schema, instance):
        self.assertFalse(validate_once(schema=schema, instance=instance))
