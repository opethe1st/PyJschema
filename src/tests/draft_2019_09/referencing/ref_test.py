import unittest

import parameterized  # type: ignore

from jschema.draft_2019_09 import validate_once


class TestRefValidate(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            (
                "ref something in $defs",
                {
                    "type": "array",
                    "$id": "https://example.com/ope",
                    "items": {"$ref": "https://example.com/ope#StringWithmax20"},
                    "$defs": {
                        "string": {
                            "$anchor": "StringWithmax20",
                            "type": "string",
                            "maxLength": 20,
                        },
                        "blah": {"$anchor": "blah", "type": "number"},
                    },
                },
                ["12345", "67890"],
            ),
            (
                "ref something in $defs with relative pointer",
                {
                    "type": "array",
                    "$id": "https://example.com/ope",
                    "items": {"$ref": "#/$defs/string"},
                    "$defs": {
                        "string": {
                            "$anchor": "StringWithmax20",
                            "type": "string",
                            "maxLength": 20,
                        },
                        "blah": {"$anchor": "blah", "type": "number"},
                    },
                },
                ["12345", "67890"],
            ),
        ]
    )
    def test_true(self, name, schema, instance):
        result = validate_once(schema=schema, instance=instance)
        self.assertTrue(result)

    @parameterized.parameterized.expand(
        [
            (
                "ref something in $defs",
                {
                    "$id": "https://example.com/ope",
                    "type": "array",
                    "items": {"$ref": "https://example.com/ope#NumberMax20"},
                    "$defs": {
                        "blah": {
                            "$anchor": "NumberMax20",
                            "type": "number",
                            "maximum": 20,
                        }
                    },
                },
                [23],
            )
        ]
    )
    def test_false(self, name, schema, instance):
        result = validate_once(schema=schema, instance=instance)
        self.assertFalse(result)
