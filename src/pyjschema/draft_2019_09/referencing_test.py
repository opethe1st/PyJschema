import unittest

from .ref import Ref
from .referencing import (
    _attach_base_URIs,
    _generate_context,
    _resolve_references
)
from .validator import Validator


class DummyValidator(Validator):
    def __init__(self, id=None, base_uri=None, validators=None, anchor=None, location=None):
        self.id = id
        self.base_uri = base_uri if base_uri else id
        self._validators = validators if validators else[]
        self.anchor = anchor
        self.location = location
        self._resolve = False

    def sub_validators(self):
        return self._validators


class Test_AttachBaseURIs(unittest.TestCase):
    # test that given a validator with just one base_uri, every validator within it has the same base_uri
    def test_one_base_uri(self):
        sub_validator1 = DummyValidator()
        sub_validator2 = DummyValidator(
            validators=[sub_validator1]
        )
        sub_validator3 = DummyValidator()

        validator_id = "http://localhost:5000/schema.json"
        validator = DummyValidator(
            id=validator_id,
            validators=[
                sub_validator3,
                sub_validator2,
            ]
        )
        _attach_base_URIs(validator=validator, parent_URI="")
        self.assertEqual(sub_validator1.base_uri, validator_id)
        self.assertEqual(sub_validator2.base_uri, validator_id)
        self.assertEqual(sub_validator3.base_uri, validator_id)
        self.assertEqual(validator.base_uri, validator_id)

    # test that given a validator with two nested base_uri this works
    def test_two_base_uri(self):
        sub_validator1 = DummyValidator()
        sub_validator_id = "http://localhost:5000/another.json"
        sub_validator2 = DummyValidator(
            id=sub_validator_id,
            validators=[sub_validator1]
        )
        sub_validator3 = DummyValidator()

        validator_id = "http://localhost:5000/schema.json"
        validator = DummyValidator(
            id=validator_id,
            validators=[
                sub_validator3,
                sub_validator2,
            ]
        )
        _attach_base_URIs(validator=validator, parent_URI="")
        self.assertEqual(sub_validator1.base_uri, sub_validator_id)
        self.assertEqual(sub_validator2.base_uri, sub_validator_id)
        self.assertEqual(sub_validator3.base_uri, validator_id)
        self.assertEqual(validator.base_uri, validator_id)

    # random test case
    def test_three_base_uri(self):
        sub_validator1 = DummyValidator()
        sub_validator2_id = "http://localhost:5000/another.json"
        sub_validator2 = DummyValidator(
            id=sub_validator2_id,
            validators=[sub_validator1]
        )
        sub_validator4 = DummyValidator()
        sub_validator3_id = "http://localhost:5000/schema124.json"
        sub_validator3 = DummyValidator(
            id=sub_validator3_id,
            validators=[sub_validator4]
        )

        validator_id = "http://localhost:5000/schema.json"
        validator = DummyValidator(
            id=validator_id,
            validators=[
                sub_validator2,
                sub_validator3,
            ]
        )
        _attach_base_URIs(validator=validator, parent_URI="")
        self.assertEqual(sub_validator1.base_uri, sub_validator2_id)
        self.assertEqual(sub_validator2.base_uri, sub_validator2_id)
        self.assertEqual(sub_validator3.base_uri, sub_validator3_id)
        self.assertEqual(sub_validator4.base_uri, sub_validator3_id)
        self.assertEqual(validator.base_uri, validator_id)

    # resolve relative id
    def test_resolve_relative_id(self):
        sub_validator1 = DummyValidator()
        sub_validator2_id = "http://localhost:5000/schema.json#anchor"
        sub_validator2 = DummyValidator(
            id="#anchor",
            validators=[sub_validator1]
        )
        sub_validator4_id = "http://localhost:5000/schema124.json#/relative/fragment"
        sub_validator4 = DummyValidator(
            id="#/relative/fragment"
        )
        sub_validator3_id = "http://localhost:5000/schema124.json"
        sub_validator3 = DummyValidator(
            id="schema124.json",
            validators=[sub_validator4]
        )

        validator_id = "http://localhost:5000/schema.json"
        validator = DummyValidator(
            id=validator_id,
            validators=[
                sub_validator2,
                sub_validator3,
            ]
        )
        _attach_base_URIs(validator=validator, parent_URI="")
        self.assertEqual(sub_validator1.base_uri, sub_validator2_id)
        self.assertEqual(sub_validator2.base_uri, sub_validator2_id)
        self.assertEqual(sub_validator3.base_uri, sub_validator3_id)
        self.assertEqual(sub_validator4.base_uri, sub_validator4_id)
        self.assertEqual(validator.base_uri, validator_id)


class Test_GenerateContext(unittest.TestCase):
    # make sure generated context is what we expect
    def test_generate_context(self):
        sub_validator1 = DummyValidator(location="schema456/schema789")
        sub_validator2_id = "http://localhost:5000/another.json"
        sub_validator2 = DummyValidator(
            id=sub_validator2_id,
            validators=[sub_validator1],
            location="schema456"
        )
        sub_validator4 = DummyValidator(
            location="schema123/schema678"
        )
        sub_validator3_id = "http://localhost:5000/schema123.json"
        sub_validator3 = DummyValidator(
            id=sub_validator3_id,
            validators=[sub_validator4],
            location="schema123"
        )

        validator_id = "http://localhost:5000/schema.json"
        validator = DummyValidator(
            id=validator_id,
            validators=[
                sub_validator2,
                sub_validator3,
            ],
            location=""
        )
        uri_to_validator = {}
        uri_to_root_location = {}

        _generate_context(validator=validator, root_base_uri=validator.base_uri, uri_to_validator=uri_to_validator, uri_to_root_location=uri_to_root_location)

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
            }
        )
        self.assertDictEqual(
            uri_to_root_location,
            {
                'http://localhost:5000/another.json': 'schema456',
                'http://localhost:5000/schema.json': '',
                'http://localhost:5000/schema123.json': 'schema123',
            }
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
        validator = DummyValidator(
            validators=[
                sub_validator1,
                sub_validator2,
            ]
        )

        self.assertFalse(sub_validator1.resolved)
        self.assertFalse(sub_validator2.resolved)

        _resolve_references(validator=validator, uri_to_validator={})

        self.assertTrue(sub_validator1.resolved)
        self.assertTrue(sub_validator2.resolved)
