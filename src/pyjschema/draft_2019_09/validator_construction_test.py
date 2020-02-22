import unittest

from pyjschema.exceptions import SchemaError

from .validator_construction import construct_validator


class Test(unittest.TestCase):
    def test(self):
        validator = construct_validator(True)
        validator(["blah, blah"])

    def test_schema_not_bool_or_dict(self):
        with self.assertRaises(SchemaError):
            construct_validator(["not a valid schema"])
