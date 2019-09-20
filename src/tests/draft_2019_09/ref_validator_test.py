import unittest

import parameterized

from jsonschema.common.reference_resolver import (
    Ref,
    add_context_to_ref_validators,
    generate_context
)
from jsonschema.draft_2019_09 import Validator, build_validator
from jsonschema.draft_2019_09.string import String


class TestBuildValidator(unittest.TestCase):

    @parameterized.parameterized.expand(
        [
            (
                "make sure there is a ref validator",
                {
                    "$ref": "#blah"
                },
            ),
        ]
    )
    def test(self, name, schema):
        ref = build_validator(schema)
        self.assertEqual(ref, Ref("#blah"))


class TestGenerateContext(unittest.TestCase):

    @parameterized.parameterized.expand(
        [
            (
                "make sure context is generated properly",
                {
                    "$anchor": "#blah",
                    "type": "string",
                },
                {"#blah"},
            ),
            (
                "make sure context is generated properly with nested anchors",
                {
                    "$anchor": "#anarray",
                    "type": "array",
                    "items": [
                        {
                            "$anchor": "#astring",
                            "type": "string",
                        },
                        {
                            "$anchor": "#anumber",
                            "type": "number",
                        },
                        {
                            "$anchor": "#anobject",
                            "type": "object",
                        },
                    ]
                },
                {"#anarray", "#astring", "#anumber", "#anobject"}
            ),
        ]
    )
    def test(self, name, schema, keys):
        validator = build_validator(schema=schema)
        context = generate_context(validator)
        self.assertEqual(
            set(context.keys()),
            keys,
        )


class TestAddContextToSchemaValidator(unittest.TestCase):

    @parameterized.parameterized.expand(
        [
            (
                "make sure we add the context to add references",
                {
                    "$ref": "#blah"
                },
            ),
        ]
    )
    def test(self, name, schema):
        ref = build_validator(schema)
        validator = Validator()
        validator.add_validator(String())

        self.assertIsNone(ref.context)

        add_context_to_ref_validators(ref, context={"#blah": validator})

        self.assertIsNotNone(ref.context)


class TestRefValidate(unittest.TestCase):

    @parameterized.parameterized.expand(
        [
            (
                "make sure we add the context to add references",
                {
                    "$ref": "#blah"
                },
            ),
        ]
    )
    def test_true(self, name, schema):
        ref = build_validator(schema)
        string_instance_validator = Validator()
        string_instance_validator.add_validator(String())

        add_context_to_ref_validators(ref, context={"#blah": string_instance_validator})

        result = ref.validate("string")
        self.assertTrue(result.ok)

    @parameterized.parameterized.expand(
        [
            (
                "make sure we add the context to add references",
                {
                    "$ref": "#blah"
                },
            ),

        ]
    )
    def test_false(self, name, schema):
        ref = build_validator(schema)
        string_instance_validator = Validator()
        string_instance_validator.add_validator(String())

        add_context_to_ref_validators(ref, context={"#blah": string_instance_validator})

        result = ref.validate(12434)
        self.assertFalse(result.ok)
