import unittest

from pyjschema.draft_2019_09 import validate


class Test(unittest.TestCase):
    def test(self):
        res = validate(schema={"not": True}, instance="123")
        self.assertFalse(res)
