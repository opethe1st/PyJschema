from jschema.common import annotate

from .number import Integer, Number


class TestNumber:

    def test(self):
        validator = Number(schema=annotate({'minimum': 0, 'maximum': 10}))
        assert validator.validate(instance=5)

    def test_validate_false_for_boolean(self):
        validator = Integer(schema=annotate({'minimum': 0, 'maximum': 10}))
        assert not validator.validate(instance=False)


class TestInteger:
    def test(self):
        validator = Integer(schema=annotate({'minimum': 0, 'maximum': 10}))
        assert validator.validate(instance=2)

    def test_validate_false_for_boolean(self):
        validator = Integer(schema=annotate({'minimum': 0, 'maximum': 10}))
        assert not validator.validate(instance=False)
