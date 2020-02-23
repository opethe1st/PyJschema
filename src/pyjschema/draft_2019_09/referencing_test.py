import unittest

from .ref import Ref
from .referencing import _populate_uri_to_validator, _resolve_references
from .validator import Validator


class DummyValidator(Validator):
    def __init__(
        self, id=None, base_uri=None, validators=None, anchor=None, location=None
    ):
        self.id = id
        self.base_uri = base_uri if base_uri else id
        self._validators = validators if validators else []
        self.anchor = anchor
        self.location = location
        self._resolve = False

    def sub_validators(self):
        return self._validators


class Test_GenerateContext(unittest.TestCase):
    # make sure generated context is what we expect
    def test_generate_context(self):
        sub_validator1 = DummyValidator(location="schema456/schema789")
        sub_validator2_id = "http://localhost:5000/another.json"
        sub_validator2 = DummyValidator(
            id=sub_validator2_id, validators=[sub_validator1], location="schema456"
        )
        sub_validator4 = DummyValidator(location="schema123/schema678")
        sub_validator3_id = "http://localhost:5000/schema123.json"
        sub_validator3 = DummyValidator(
            id=sub_validator3_id, validators=[sub_validator4], location="schema123"
        )

        validator_id = "http://localhost:5000/schema.json"
        validator = DummyValidator(
            id=validator_id, validators=[sub_validator2, sub_validator3,], location=""
        )
        uri_to_validator = {}
        uri_to_root_location = {}

        _populate_uri_to_validator(
            validator=validator,
            root_base_uri=validator.base_uri,
            uri_to_validator=uri_to_validator,
            uri_to_root_location=uri_to_root_location,
        )

        self.assertDictEqual(
            uri_to_validator,
            {
                "http://localhost:5000/schema.json": validator,
                "http://localhost:5000/another.json": sub_validator2,
                "http://localhost:5000/schema123.json": sub_validator3,
                "http://localhost:5000/schema.json#schema123": sub_validator3,
                "http://localhost:5000/schema.json#schema456": sub_validator2,
                "http://localhost:5000/schema.json#schema123/schema678": sub_validator4,
                "http://localhost:5000/schema.json#schema456/schema789": sub_validator1,
            },
        )
        self.assertDictEqual(
            uri_to_root_location,
            {
                "http://localhost:5000/another.json": "schema456",
                "http://localhost:5000/schema.json": "",
                "http://localhost:5000/schema123.json": "schema123",
            },
        )


class DummyRef(Ref):
    def __init__(self):
        self.resolved = False
        self._validator = DummyValidator()

    def resolve(self, uri_to_validator):
        self.resolved = True


class Test_ResolveReferences(unittest.TestCase):
    def test(self):
        sub_validator1 = DummyRef()
        sub_validator2 = DummyRef()
        validator = DummyValidator(validators=[sub_validator1, sub_validator2,])

        self.assertFalse(sub_validator1.resolved)
        self.assertFalse(sub_validator2.resolved)

        _resolve_references(validator=validator, uri_to_validator={})

        self.assertTrue(sub_validator1.resolved)
        self.assertTrue(sub_validator2.resolved)
