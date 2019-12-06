from .string import String
from jschema.common import annotate


class TestString:

    def test_string_true(self):
        validator = String(schema=annotate({"minLength": 1, "maxLength": 5, "pattern": "a.*b.*c.*"}))
        assert validator.validate(instance="abc")

    def test_string_false(self):
        validator = String(schema=annotate({"minLength": 1, "maxLength": 5, "pattern": "abc"}))
        assert not validator.validate(instance="")
