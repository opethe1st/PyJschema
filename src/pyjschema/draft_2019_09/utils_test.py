import unittest
from .utils import to_canonical_uri
import parameterized


class TestToCanonicalURI(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            (
                "with scheme and authority",
                "http://localhost:5000/root.json",
                "http://localhost:5000/other.json",
                "http://localhost:5000/other.json",
            ),
            (
                "with anchor",
                "http://localhost:5000/root.json",
                "http://localhost:5000/root.json#other",
                "http://localhost:5000/root.json#other",
            ),
            (
                "with just anchor fragment",
                "http://localhost:5000/root.json",
                "#other",
                "http://localhost:5000/root.json#other",
            ),
            (
                "with empty anchor fragment",
                "http://localhost:5000/root.json",
                "#",
                "http://localhost:5000/root.json#",
            ),
            (
                "with json pointer",
                "http://localhost:5000/root.json",
                "#/path/to/other",
                "http://localhost:5000/root.json#/path/to/other",
            ),
            (
                "with path",
                "http://localhost:5000/root.json",
                "/path/to/other.json",
                "http://localhost:5000/path/to/other.json",
            ),
        ]
    )
    def test(self, description, current_base_uri, uri, expected_uri):
        uri = to_canonical_uri(current_base_uri=current_base_uri, uri=uri)
        self.assertEqual(uri, expected_uri)
