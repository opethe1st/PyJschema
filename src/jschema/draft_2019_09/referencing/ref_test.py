import unittest

import parameterized  # type: ignore

from .ref import resolve_uri


class TestResolveURI(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            (
                "resolve uri of embedded base_uri + fragment",
                {
                    "https://example.com/root.json": True,
                    "https://example.com/other.json": False,
                    "#/$defs/other/defs/string": None,
                },
                {'https://example.com/other.json': '#/$defs/other'},
                "https://example.com/other.json#/defs/string",
                None,
            ),
            (
                "resolve uri of root base uri",
                {
                    "https://example.com/root.json": True,
                    "https://example.com/other.json": False,
                    "#/$defs/other/defs/string": None,
                },
                {'https://example.com/other.json': '#/$defs/other'},
                "https://example.com/root.json",
                True,
            ),
            (
                "resolve uri of root base uri + fragment",
                {
                    "https://example.com/root.json": True,
                    "https://example.com/other.json": False,
                    "#/$defs/other": False,
                },
                {'https://example.com/other.json': '#/$defs/other'},
                "https://example.com/root.json#/$defs/other",
                False,
            ),
            (
                "resolve uri of embedded base uri",
                {
                    "https://example.com/root.json": True,
                    "https://example.com/other.json": False,
                    "#/$defs/other/defs/string": None,
                },
                {'https://example.com/other.json': '#/$defs/other'},
                "https://example.com/other.json",
                False,
            ),
        ]
    )
    def test(self, description, context, base_uri_to_abs_location, input_, output):
        self.assertEqual(
            resolve_uri(
                context=context,
                base_uri_to_abs_location=base_uri_to_abs_location,
                uri=input_
            ),
            output
        )
