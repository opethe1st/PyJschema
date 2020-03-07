import unittest

import parameterized

from pyjschema.draft_2019_09 import validate


class TestNumber(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            ("is number", {"$id": "https://example.com/ope", "type": "number"}, 123),
            (
                "multipleOf",
                {"$id": "https://example.com/ope", "type": "number", "multipleOf": 3},
                123,
            ),
            (
                "minimum",
                {"$id": "https://example.com/ope", "type": "number", "minimum": 3},
                3,
            ),
            (
                "exclusiveMinimum",
                {
                    "$id": "https://example.com/ope",
                    "type": "number",
                    "exclusiveMinimum": 3,
                },
                4,
            ),
            (
                "maximum",
                {"$id": "https://example.com/ope", "type": "number", "maximum": 3},
                3,
            ),
            (
                "exclusiveMaximum",
                {
                    "$id": "https://example.com/ope",
                    "type": "number",
                    "exclusiveMaximum": 5,
                },
                4,
            ),
            ("integer", {"$id": "https://example.com/ope", "type": "integer"}, 4),
        ]
    )
    def test_true(self, name, schema, instance):
        self.assertTrue(validate(schema=schema, instance=instance))

    @parameterized.parameterized.expand(
        [
            (
                "is not number",
                {"$id": "https://example.com/ope", "type": "number"},
                "123",
            ),
            (
                "multipleOf",
                {"$id": "https://example.com/ope", "type": "number", "multipleOf": 4},
                123,
            ),
            (
                "minimum",
                {"$id": "https://example.com/ope", "type": "number", "minimum": 124},
                123,
            ),
            (
                "exclusiveMinimum",
                {
                    "$id": "https://example.com/ope",
                    "type": "number",
                    "exclusiveMinimum": 124,
                },
                124,
            ),
            (
                "maximum",
                {"$id": "https://example.com/ope", "type": "number", "maximum": 123},
                124,
            ),
            (
                "exclusiveMaximum",
                {
                    "$id": "https://example.com/ope",
                    "type": "number",
                    "exclusiveMaximum": 124,
                },
                124,
            ),
            ("integer", {"$id": "https://example.com/ope", "type": "integer"}, 124.012),
        ]
    )
    def test_false(self, name, schema, instance):
        self.assertFalse(validate(schema=schema, instance=instance))
