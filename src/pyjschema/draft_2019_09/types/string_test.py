import unittest

from .string import String


class TestString(unittest.TestCase):
    def test_string_true(self):
        validator = String(
            schema={"minLength": 1, "maxLength": 5, "pattern": "a.*b.*c.*"}
        )
        assert validator.validate(instance="abc")

    def test_string_false(self):
        validator = String(
            schema={"minLength": 1, "maxLength": 5, "pattern": "abc"}
        )
        assert not validator.validate(instance="")
