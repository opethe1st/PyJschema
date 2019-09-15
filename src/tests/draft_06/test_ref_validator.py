import unittest

import parameterized

from jsonschema.common.reference_resolver import (
    Ref,
    add_context_to_ref_validators,
    generate_context
)
from jsonschema.draft_06 import build_validator
from jsonschema.draft_06.composite import Validator
from jsonschema.draft_06.string import String


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
                    "$id": "#blah",
                    "type": "string",
                },
            ),
        ]
    )
    def test(self, name, schema):
        validator = build_validator(schema=schema)
        context = generate_context(validator)
        self.assertEqual(
            set(context.keys()),
            {"#blah"}
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
