import unittest

import parameterized

from .validator import all_keywords
from jsonschema.common import Type, Keyword

class ATypeClass(Type):
    KEYWORDS_TO_VALIDATOR = {
        ("aKeyword", "anotherKeyword"): Keyword,
        ("bKeyword",): Keyword,
        ("cKeyword",): Keyword,
    }

class TestAllKeywords(unittest.TestCase):

    def test_array(self):
        keywords = all_keywords(ATypeClass)
        self.assertEqual(
            keywords,
            {"aKeyword", "anotherKeyword", "bKeyword", "cKeyword"}
        )
