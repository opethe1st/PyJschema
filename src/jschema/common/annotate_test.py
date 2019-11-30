import unittest

import parameterized  # type: ignore

from jschema.common import Primitive, Dict, List
from jschema.common.annotate import annotate, deannotate


class TestAnnotate(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            ("empty string", "", Primitive("", "#")),
            ("string", "str", Primitive("str", "#")),
            ("array with one item", ["item"], List([Primitive("item", "#/0")], "#")),
            (
                "dictionary with one item",
                {"key": "value"},
                Dict({"key": Primitive("value", "#/key")}, location="#"),
            ),
            (
                "dictionary with more than one item",
                {"key": "value", "key2": 2},
                Dict(
                    {
                        "key": Primitive("value", "#/key"),
                        "key2": Primitive(2, "#/key2"),
                    },
                    location="#",
                ),
            ),
            (
                "nested array",
                ["item", ["item1", "item2"]],
                List(
                    [
                        Primitive("item", "#/0"),
                        List(
                            [Primitive("item1", "#/1/0"), Primitive("item2", "#/1/1")],
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


class TestDeAnnotate(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            ("empty string", ""),
            ("string", "str"),
            ("array with one item", ["item"]),
            (
                "dictionary with one item",
                {"key": "value"},
            ),
            (
                "dictionary with more than one item",
                {"key": "value", "key2": 2},
            ),
            (
                "nested array",
                ["item", ["item1", "item2"]],
            ),
        ]
    )
    def test_true(self, name, obj,):
        res = deannotate(annotate(obj=obj))
        self.assertEqual(res, obj)
