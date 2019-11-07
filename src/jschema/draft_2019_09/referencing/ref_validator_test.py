import unittest

import parameterized  # type: ignore

from jschema.common.annotate import annotate
from jschema.draft_2019_09 import build_validator, validate_once

from .reference_resolver import (
    attach_base_URIs,
    generate_context
)


class TestGenerateContext(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            (
                "make sure context is generated properly",
                {"$anchor": "blah", "type": "string", "$id": "https://example.com/ope"},
                {"https://example.com/ope", "https://example.com/ope#blah", "#"},
            ),
            (
                "make sure context is generated properly with nested anchors",
                {
                    "$id": "https://example.com/ope",
                    "$anchor": "anarray",
                    "type": "array",
                    "items": [
                        {"$anchor": "astring", "type": "string"},
                        {"$anchor": "anumber", "type": "number"},
                        {"$anchor": "anobject", "type": "object"},
                    ],
                },
                {
                    "https://example.com/ope",
                    "https://example.com/ope#anarray",
                    "https://example.com/ope#astring",
                    "https://example.com/ope#anumber",
                    "https://example.com/ope#anobject",
                    "#/items/2",
                    "#/items/0",
                    "#",
                    "#/items/1",
                },
            ),
        ]
    )
    def test(self, name, schema, keys):
        validator = build_validator(schema=annotate(obj=schema))
        attach_base_URIs(validator=validator, parent_URI=schema["$id"])
        context = generate_context(validator)
        self.assertEqual(set(context.keys()), keys)


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
        self.assertTrue(result.ok)

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
        self.assertFalse(result.ok)
