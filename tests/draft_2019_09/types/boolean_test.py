import unittest

import parameterized

from pyjschema.draft_2019_09 import validate


class TestBoolean(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            ("true", {"$id": "https://example.com/ope", "type": "boolean"}, True),
            ("boolean", {"$id": "https://example.com/ope", "type": "boolean"}, False),
        ]
    )
    def test_instance_true(self, name, schema, instance):
        self.assertTrue(validate(schema=schema, instance=instance))

    def test_instance_not_boolean(self):
        res = validate(
            schema={"$id": "https://example.com/ope", "type": "boolean"}, instance=123
        )
        self.assertFalse(res)
