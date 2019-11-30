import unittest

import parameterized

from jschema.draft_2019_09 import validate_once


class TestString(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            (
                "is a string",
                {"$id": "https://example.com/ope", "type": "string"},
                "abc",
            ),
            (
                "pattern",
                {"$id": "https://example.com/ope", "type": "string", "pattern": "abc"},
                "abcmatch",
            ),
            (
                "all keywords",
                {
                    "$id": "https://example.com/ope",
                    "type": "string",
                    "pattern": "abc",
                    "minLength": 1,
                    "maxLength": 10,
                },
                "abcmatch",
            ),
        ]
    )
    def test_true(self, name, schema, instance):
        self.assertTrue(validate_once(schema=schema, instance=instance))

    @parameterized.parameterized.expand(
        [
            ("not a string", {"$id": "https://example.com/ope", "type": "string"}, 123),
            (
                "mininum",
                {"$id": "https://example.com/ope", "type": "string", "minLength": 100},
                "tooshort",
            ),
            (
                "maximum",
                {"$id": "https://example.com/ope", "type": "string", "maxLength": 1},
                "toolong",
            ),
            (
                "pattern",
                {"$id": "https://example.com/ope", "type": "string", "pattern": "abc"},
                "123match",
            ),
        ]
    )
    def test_false(self, name, schema, instance):
        self.assertFalse(validate_once(schema=schema, instance=instance))
