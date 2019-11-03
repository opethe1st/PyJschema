import unittest

import parameterized

from jsonschema.draft_2019_09 import validate_once


class TestBoolean(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            ("true", {"$id": "https://example.com/ope", "type": "boolean"}, True),
            ("boolean", {"$id": "https://example.com/ope", "type": "boolean"}, False),
        ]
    )
    def test_instance_true(self, name, schema, instance):
        self.assertTrue(validate_once(schema=schema, instance=instance).ok)

    def test_instance_not_boolean(self):
        ok = validate_once(
            schema={"$id": "https://example.com/ope", "type": "boolean"}, instance=123
        ).ok
        self.assertFalse(ok)
