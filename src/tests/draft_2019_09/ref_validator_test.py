import unittest

import parameterized

from jsonschema.common.reference_resolver import (
    Ref,
    add_context_to_ref_validators,
    generate_context,
    attach_base_URIs,
)
from jsonschema.draft_2019_09 import Validator, build_validator, validate_once
from jsonschema.draft_2019_09.string import String


class TestBuildValidator(unittest.TestCase):
    @parameterized.parameterized.expand(
        [("make sure there is a ref validator", {"$ref": "#blah"})]
    )
    def test(self, name, schema):
        ref = build_validator(schema)
        self.assertEqual(ref, Ref("#blah"))


class TestGenerateContext(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            (
                "make sure context is generated properly",
                {"$anchor": "blah", "type": "string", "$id": "https://example.com/ope",},
                {
                    "https://example.com/ope",
                    "https://example.com/ope#blah"
                },
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
                },
            ),
        ]
    )
    def test(self, name, schema, keys):
        validator = build_validator(schema=schema)
        attach_base_URIs(validator=validator, parent_URI=schema["$id"])
        context = generate_context(validator)
        self.assertEqual(set(context.keys()), keys)


class TestAddContextToSchemaValidator(unittest.TestCase):
    @parameterized.parameterized.expand(
        [("make sure we add the context to add references", {"$ref": "#blah"})]
    )
    def test(self, name, schema):
        #  not sure this is a valid test
        ref = build_validator(schema)
        validator = Validator()
        validator.add_validator(String(schema))

        self.assertIsNone(ref.context)

        add_context_to_ref_validators(ref, context={"#blah": validator})

        self.assertIsNotNone(ref.context)


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
            )
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
