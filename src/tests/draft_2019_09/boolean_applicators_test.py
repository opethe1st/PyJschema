import unittest

import parameterized

from jschema.draft_2019_09 import validate_once


class TestBooleanLogic(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            (
                "if condition true",
                {
                    "$id": "mysite",
                    "if": {"type": "string"},
                    "then": {"type": "string", "maxLength": 40},
                    "else": {"type": "number", "maximum": 5},
                },
                "some string",
            ),
            (
                "if condition false",
                {
                    "$id": "mysite",
                    "if": {"type": "string"},
                    "then": {"type": "string", "maxLength": 40},
                    "else": {"type": "number", "maximum": 5},
                },
                4,
            ),
        ]
    )
    def test_true(self, name, schema, instance):
        res = validate_once(schema, instance)
        self.assertTrue(res.ok)

    @parameterized.parameterized.expand(
        [
            (
                "if condition true",
                {
                    "$id": "mysite",
                    "if": {"type": "string"},
                    "then": {"type": "string", "maxLength": 4},
                    "else": {"type": "number", "maximum": 5},
                },
                "string too long",
            ),
            (
                "if condition false",
                {
                    "$id": "mysite",
                    "if": {"type": "string"},
                    "then": {"type": "string", "maxLength": 4},
                    "else": {"type": "number", "maximum": 5},
                },
                100,
            ),
        ]
    )
    def test_false(self, name, schema, instance):
        res = validate_once(schema, instance)
        self.assertFalse(res.ok)
