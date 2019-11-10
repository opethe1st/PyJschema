import unittest

import parameterized  # type: ignore

from jschema.common.annotate import annotate
from jschema.draft_2019_09 import build_validator

from .reference_resolver import (
    attach_base_URIs,
    generate_context,
    get_base_URI_from_URI_part,
    resolve_uri,
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
                {"https://example.com/ope", "https://example.com/ope#blah", "https://example.com/ope#"},
                [("https://example.com/ope", "https://example.com/ope#")]
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
                    "https://example.com/anobject",
                    "https://example.com/ope",
                    'https://example.com/ope#',
                    'https://example.com/ope#/items/0',
                    'https://example.com/ope#/items/1',
                    'https://example.com/ope#/items/2',
                    'https://example.com/ope#/items/2/properties/abc',
                    "https://example.com/ope#anarray",
                    "https://example.com/ope#astring",
                    "https://example.com/ope#anumber",
                },
                [
                    ('https://example.com/ope#/items/0', "https://example.com/ope#astring"),
                    ('https://example.com/ope#/items/1', "https://example.com/ope#anumber"),
                    ('https://example.com/ope#/items/2', "https://example.com/anobject"),
                    ('https://example.com/ope', "https://example.com/ope#"),
                ]
            ),
        ]
    )
    def test(self, name, schema, keys, same_keys):
        validator = build_validator(schema=annotate(obj=schema))
        attach_base_URIs(validator=validator, parent_URI=schema["$id"])
        context = generate_context(validator, root_base_uri=schema["$id"])

        self.assertSetEqual(set(context.keys()), keys)

        for ref1, ref2 in same_keys:
            self.assertEqual(context[ref1], context[ref2])


class TestResolveURI(unittest.TestCase):
    @parameterized.parameterized.expand([
        (
            "description",
            {"https://example.com/root.json/": True},
            "https://example.com/other.json#/defs/string",
            "https://example.com/root.json/$defs/other/defs/string"
        ),
    ])
    def test(self, description, context, input_, output):
        self.assertEqual(resolve_uri(context=context, uri=input_), output)
