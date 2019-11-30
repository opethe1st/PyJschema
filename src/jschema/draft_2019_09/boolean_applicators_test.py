import unittest

from jschema.draft_2019_09 import validate_once


class Test(unittest.TestCase):
    def test(self):
        res = validate_once(schema={"not": True}, instance="123")
        self.assertFalse(res)
