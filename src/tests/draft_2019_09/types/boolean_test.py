import unittest

import parameterized

from jschema.draft_2019_09 import validate_once


class TestBoolean(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            ("true", {"$id": "https://example.com/ope", "type": "boolean"}, True),
            ("boolean", {"$id": "https://example.com/ope", "type": "boolean"}, False),
        ]
    )
    def test_instance_true(self, name, schema, instance):
        self.assertTrue(validate_once(schema=schema, instance=instance))

    def test_instance_not_boolean(self):
        res = validate_once(
            schema={"$id": "https://example.com/ope", "type": "boolean"}, instance=123
        )
        self.assertFalse(res)
