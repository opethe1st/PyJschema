import unittest

import parameterized  # type: ignore

from jsonschema.common import Instance
from jsonschema.common.annotate import annotate


class TestAnnotate(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            ("empty string", "", Instance("", "#")),
            ("string", "str", Instance("str", "#")),
            ("array with one item", ["item"], Instance([Instance("item", "#/0")], "#")),
            (
                "dictionary with one item",
                {"key": "value"},
                Instance({"key": Instance("value", "#/key")}, location="#"),
            ),
            (
                "dictionary with more than one item",
                {"key": "value", "key2": "value2"},
                Instance(
                    {
                        "key": Instance("value", "#/key"),
                        "key2": Instance("value2", "#/key2"),
                    },
                    "#",
                ),
            ),
            (
                "nested array",
                ["item", ["item1", "item2"]],
                Instance(
                    [
                        Instance("item", "#/0"),
                        Instance(
                            [Instance("item1", "#/1/0"), Instance("item2", "#/1/1")],
                            "#/1",
                        ),
                    ],
                    "#",
                ),
            ),
        ]
    )
    def test_true(self, name, obj, instance):
        res = annotate(obj=obj)
        self.assertEqual(res, instance)
