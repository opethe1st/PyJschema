import unittest

import parameterized

from .validator_construction import build_validator_and_resolve_references


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
            "$schema": "schema",
            "$id": "https://example.com/schema",
            "$ref": "tree",
            "$defs": {
                "tree": {
                    "$id": "tree",
                    "type": "object",
                    "properties": {
                        "data": True,
                        "children": {
                            "type": "array",
                            "items": {"$ref": "tree"},
                        }
                    },
                    "required": ["data", "children"]
                }
            }
        }

        validator, uri_to_validator = build_validator_and_resolve_references(schema=schema)

        self.assertEqual(
            result,
            bool(validator.validate(instance=instance)),
        )


# hm, recursiveRef only works if there is the ability to combine with ref with adjacent keywords.
# is this too difficult?
class TestRecursiveRef(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            ({"data": [{"data": "innner data"}], "children": []}, True),

        ]
    )
    def test_recursive_ref(self, instance, result):
        schema = {
            "$schema": "schema",
            "$id": "https://example.com/schema",
            "$ref": "tree",
            "$defs": {
                "tree": {
                    "$id": "tree",
                    "type": "object",
                    "properties": {
                        "data": True,
                        "children": {
                            "type": "array",
                            "items": {"$ref": "tree"},
                        }
                    },
                    "required": ["data", "children"]
                }
            }
        }

        validator, uri_to_validator = build_validator_and_resolve_references(schema=schema)

        self.assertEqual(
            result,
            bool(validator.validate(instance=instance)),
        )
