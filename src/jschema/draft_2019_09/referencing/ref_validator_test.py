import unittest

import parameterized  # type: ignore

from jschema.common.annotate import annotate
from jschema.draft_2019_09 import build_validator, validate_once
from jschema.draft_2019_09.validator_construction import build_validator_and_attach_context
from .reference_resolver import (
    attach_base_URIs,
    generate_context,
    get_base_URI_from_URI_part,
)


class TestGetBaseURIfromURIpart(unittest.TestCase):

    @parameterized.parameterized.expand([
        ("https://localhost:1234/root", "other", "https://localhost:1234/other"),
        ("https://localhost:1234/root.json", "other.json", "https://localhost:1234/other.json"),
        ("https://localhost:1234/root.json", "t/other.json", "https://localhost:1234/t/other.json"),
        ("https://localhost:1234/root.json", "abcdef/other.json", "https://localhost:1234/abcdef/other.json"),
    ])
    def test(self, parent_URI, base_URI, result):
        self.assertEqual(
            get_base_URI_from_URI_part(parent_URI=parent_URI, base_URI=base_URI),
            result
        )


class TestAttachBaseURI(unittest.TestCase):

    @parameterized.parameterized.expand([
        (
            "make sure that the expected base_URI are set",
            {
                "$id": "http://localhost:1234/root#"
            },
            {"http://localhost:1234/root"},
        ),
        (
            "make sure that the expected base_URI are set",
            {
                "$id": "http://localhost:1234/root",
                "type": "array",
                "items": {
                    "$id": "items"
                }
            },
            {"http://localhost:1234/root", "http://localhost:1234/items"}
        ),
        (
            "make sure that the expected base_URI are set",
            {
                "$id": "http://localhost:1234/root.json#",
                "type": "array",
                "items": {
                    "$id": "/items/abc.json"
                }
            },
            {"http://localhost:1234/root.json", "http://localhost:1234/items/abc.json"}
        ),
    ])
    def test(self, description, schema, base_uris):
        validator = build_validator(schema=annotate(obj=schema))
        attach_base_URIs(validator=validator, parent_URI=schema["$id"].rstrip("#"))
        self.assertEqual(get_base_uris(validator=validator), base_uris)


def get_base_uris(validator):
    uris = {validator.id}
    for subvalidator in validator.subschema_validators():
        uris |= get_base_uris(subvalidator)
    return uris


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
                        {
                            "$id": "anobject",
                            "type": "object",
                            "properties": {
                                "abc": True
                            }
                        },
                    ],
                },
                {
                    'https://example.com/ope#/items/1',
                    'https://example.com/ope#',
                    'https://example.com/ope#/items/2',
                    'https://example.com/ope#/items/0',
                    'https://example.com/ope#/items/2/properties/abc',
                    "https://example.com/ope",
                    "https://example.com/ope#anarray",
                    "https://example.com/ope#astring",
                    "https://example.com/ope#anumber",
                    "https://example.com/anobject",
                },
            ),
        ]
    )
    def test(self, name, schema, keys):
        validator = build_validator(schema=annotate(obj=schema))
        attach_base_URIs(validator=validator, parent_URI=schema["$id"])
        context = generate_context(validator, root_base_uri=schema["$id"])
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


class Test(unittest.TestCase):

    def test_xxx(self):
        schema = {
            "type": "array",
            "$id": "https://example.com/ope",
            "items": [{"$ref": "#/$defs/string"}],
            "additionalItems": {"$ref": "#blah"},
            "$defs": {
                "string": {
                    "$anchor": "StringWithmax20",
                    "type": "string",
                    "maxLength": 20,
                },
                "blah": {"$anchor": "blah", "type": "number"},
            },
        }
        validator, context = build_validator_and_attach_context(
            schema=schema
        )
        assert validator.validate(
            ["01234567890123456789", 123]
        ).ok

    def test_yyy(self):
        schema = {
            "$id": "http://localhost:1234/tree",
            "type": "object",
            "properties": {
                "meta": {"type": "string"},
                "nodes": {
                    "type": "array",
                    "items": {"$ref": "node"}
                }
            },
            "required": ["meta", "nodes"],
            "$defs": {
                "node": {
                    "$id": "http://localhost:1234/node",
                    "type": "object",
                    "properties": {
                        "value": {"type": "number"},
                        "subtree": {"$ref": "tree"}
                    },
                    "required": ["value"]
                }
            }
        }
        validator, context = build_validator_and_attach_context(
            schema=schema
        )
        instance = {
            "meta": "root",
            "nodes": [
                {
                    "value": 1,
                }
            ]
        }
        res = validator.validate(instance=instance)
        assert res.ok
