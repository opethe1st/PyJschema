from jschema.common import annotate
from .types_validator import Types


class TestTypes:

    def test_types_true(self):
        validator = Types(schema=annotate({"maxLength": 10, "maximum": 4}))

        assert validator.validate(instance="astring")
        assert validator.validate(instance=3)

    def test_types_list(self):
        validator = Types(schema=annotate({"types": ["integer", "string"]}))

        assert validator.validate(instance="astring")
        assert validator.validate(instance=3)
