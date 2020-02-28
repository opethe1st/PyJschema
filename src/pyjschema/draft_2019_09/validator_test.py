import unittest

import parameterized

from pyjschema.exceptions import SchemaError

from .validator import Validator
from .validator_construction import construct_validator


class TestValidator(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            ({"data": [{"data": "innner data"}], "children": []}, True),
            ({"data": True, "children": [{"notdata": ""}]}, False),
            ({"data": True, "children": [{"notdata": ""}]}, False),
        ]
    )
    def test_recursive_ref(self, instance, result):
        schema = {
            "$id": "https://example.com/schema",
            "$ref": "tree",
            "$defs": {
                "tree": {
                    "$id": "tree",
                    "type": "object",
                    "properties": {
                        "data": True,
                        "children": {"type": "array", "items": {"$ref": "tree"},},
                    },
                    "required": ["data", "children"],
                }
            },
        }

        validator = construct_validator(schema=schema)

        self.assertEqual(
            result, bool(validator(instance=instance)),
        )

    @parameterized.parameterized.expand(
        ["unevaluatedProperties", "unevaluatedItems",]
    )
    def test_unsupported_keywords(self, keyword):
        with self.assertRaises(SchemaError):
            Validator(schema={keyword: True})


class TestRecursiveRef(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            ({"data": [{"data": "innner data"}]}, True),
            ({"data": [{"data": "innner data"}], "anotherProperty": []}, False),
        ]
    )
    def test_recursive_ref(self, instance, result):
        schema = {
            "$id": "https://example.com/schema",
            "$ref": "tree",
            "$recursiveAnchor": False,
            "maxProperties": 1,
            "$defs": {
                "tree": {
                    "$id": "tree",
                    "$recursiveAnchor": False,
                    "type": "object",
                    "properties": {
                        "data": True,
                        "children": {
                            "$recursiveAnchor": True,
                            "type": "array",
                            "items": {"$recursiveRef": "#"},
                        },
                    },
                }
            },
        }

        validator = construct_validator(schema=schema)

        self.assertEqual(
            result, bool(validator(instance=instance)),
        )
