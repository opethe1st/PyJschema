import unittest

import parameterized

from jschema.draft_2019_09 import validate_once


class TestRejectAll(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            ("random int", False, 1234),
            ("random string", False, "1234"),
            ("null", False, None),
            ("false", False, False),
            ("array with different stuff", False, [False, 1, "1224"]),
            ("object with different stuff", False, {"k1": 123, "k2": "v1"}),
        ]
    )
    def test_true(self, name, schema, instance):
        self.assertFalse(validate_once(schema=schema, instance=instance).ok)
