import unittest

import parameterized

from pyjschema.draft_2019_09 import validate_once


class TestTrue(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            ("random int", True, 1234),
            ("random string", True, "1234"),
            ("null", True, None),
            ("false", True, False),
            ("array with different stuff", True, [False, 1, "1224"]),
            ("object with different stuff", True, {"k1": 123, "k2": "v1"}),
        ]
    )
    def test_true(self, name, schema, instance):
        self.assertTrue(validate_once(schema=schema, instance=instance))

    @parameterized.parameterized.expand(
        [
            ("random int", {"$id": "https://example.com/ope"}, 1234),
            ("random string", {"$id": "https://example.com/ope"}, "1234"),
            ("null", {"$id": "https://example.com/ope"}, None),
            ("false", {"$id": "https://example.com/ope"}, False),
            (
                "array with different stuff",
                {"$id": "https://example.com/ope"},
                [False, 1, "1224"],
            ),
            (
                "object with different stuff",
                {"$id": "https://example.com/ope"},
                {"k1": 123, "k2": "v1"},
            ),
        ]
    )
    def test_empty_schema(self, name, schema, instance):
        self.assertTrue(validate_once(schema=schema, instance=instance))
