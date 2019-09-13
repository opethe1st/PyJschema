from jsonschema.draft_06.validator import build_validator
import unittest


def validate(schema, instance) -> bool:
    return build_validator(schema=schema).validate(instance).ok


# Test that the enumValidator works
class TestEnum(unittest.TestCase):
    def test_instance_in_enum(self):
        ok = validate(
            schema={
                "enum": [
                    "Abc",
                    1224,
                ]
            },
            instance="Abc",
        )
        self.assertTrue(ok)

    def test_instance_not_in_enum(self):
        ok = validate(
            schema={
                "enum": [
                    "Abc",
                    1244
                ]
            },
            instance=123,
        )
        self.assertFalse(ok)


# test that the constValidator works
class TestConst(unittest.TestCase):
    def test_instance_equal_const(self):
        ok = validate(
            schema={
                "const": "ABC"
            },
            instance="ABC",
        )
        self.assertTrue(ok)

    def test_instance_not_equal_const(self):
        ok = validate(
            schema={
                "const": "DEF"
            },
            instance=123,
        )
        self.assertFalse(ok)


class TestNull(unittest.TestCase):
    def test_instance_null(self):
        ok = validate(
            schema={
                "type": "null"
            },
            instance=None,
        )
        self.assertTrue(ok)

    def test_instance_not_null(self):
        ok = validate(
            schema={
                "type": "null"
            },
            instance=123,
        )
        self.assertFalse(ok)


class TestString(unittest.TestCase):
    def test_is_a_string(self):
        ok = validate(
            schema={
                "type": "string"
            },
            instance="abc",
        )
        self.assertTrue(ok)

    def test_not_a_string(self):
        ok = validate(
            schema={
                "type": "string"
            },
            instance=123,
        )
        self.assertFalse(ok)

    def test_less_than_minimum(self):
        ok = validate(
            schema={'type': "string", "minLength": 100},
            instance="tooshort"
        )
        self.assertFalse(ok)

    def test_more_than_minimum(self):
        ok = validate(
            schema={'type': "string", "maxLength": 1},
            instance="tooslong"
        )
        self.assertFalse(ok)

    def test_not_matching_pattern(self):
        ok = validate(
            schema={'type': "string", "pattern": "abc"},
            instance="123match"
        )
        self.assertFalse(ok)

    def test_matching_pattern(self):
        ok = validate(
            schema={'type': "string", "pattern": "abc"},
            instance="abcmatch"
        )
        self.assertTrue(ok)

    def test_all_keyword_valid(self):
        ok = validate(
            schema={'type': "string", "pattern": "abc", "minLength": 1, "maxLength": 10},
            instance="abcmatch"
        )
        self.assertTrue(ok)


class TestBoolean(unittest.TestCase):
    def test_instance_true(self):
        ok = validate(
            schema={
                "type": "boolean"
            },
            instance=True,
        )
        self.assertTrue(ok)

    def test_instance_false(self):
        ok = validate(
            schema={
                "type": "boolean"
            },
            instance=False,
        )
        self.assertTrue(ok)

    def test_instance_not_boolean(self):
        ok = validate(
            schema={
                "type": "boolean"
            },
            instance=123,
        )
        self.assertFalse(ok)


# test that the numberValidator works - success and failure - not implemented yet
# test that the instanceValidator works - success and failure
