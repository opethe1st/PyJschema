import unittest

from .types_validator import Types


class TestTypes(unittest.TestCase):
    def test_types_true(self):
        validator = Types(schema={"maxLength": 10, "maximum": 4})

        assert validator.validate(instance="astring")
        assert validator.validate(instance=3)

    def test_types_list(self):
        validator = Types(schema={"types": ["integer", "string"]})

        assert validator.validate(instance="astring")
        assert validator.validate(instance=3)
