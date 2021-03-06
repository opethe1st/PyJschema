import unittest

from pyjschema.exceptions import ProgrammerError, SchemaError

from .ref import RecursiveRef, Ref
from .validator import Validator


class DummyValidator(Validator):
    def __init__(self, parent=None, recursiveAnchor=False):
        self.parent = parent
        self.recursiveAnchor = recursiveAnchor

    def __call__(self, instance, location):
        return True


class TestRefResolve(unittest.TestCase):
    def test(self):
        ref = Ref(schema={"$ref": "other.json"}, location="", parent=None)
        ref.base_uri = "https://localhost:5000/root.json"
        validator = DummyValidator()

        ref.resolve(uri_to_validator={"https://localhost:5000/other.json": validator})

        self.assertEqual(ref._validator, validator)

    def test_unknown_validator(self):
        ref = Ref(schema={"$ref": "other.json"}, location="", parent=None)
        ref.base_uri = "https://localhost:5000/root.json"
        validator = DummyValidator()

        with self.assertRaises(SchemaError):
            ref.resolve(
                uri_to_validator={"https://localhost:5000/blah.json": validator}
            )


class TestRecursiveRef(unittest.TestCase):
    def test_is_root(self):
        validator = DummyValidator()
        recursiveRef = RecursiveRef(
            schema={"$recursiveRef": "#"}, location="", parent=validator
        )

        recursiveRef.resolve()

        self.assertEqual(recursiveRef._validator, validator)

    def test_is_not_root(self):
        parent = DummyValidator()
        validator = DummyValidator(parent=parent, recursiveAnchor=False)
        recursiveRef = RecursiveRef(
            schema={"$recursiveRef": "#"}, location="", parent=validator
        )

        recursiveRef.resolve()

        self.assertEqual(recursiveRef._validator, validator)

    @unittest.expectedFailure
    def test_use_top_parent_false(self):
        parent = DummyValidator(recursiveAnchor=False)
        # immediate parent is ignored
        validator = DummyValidator(parent=parent, recursiveAnchor=False)
        recursiveRef = RecursiveRef(
            schema={"$recursiveRef": "#"}, location="", parent=validator
        )

        recursiveRef.resolve()

        self.assertEqual(recursiveRef._validator, parent)

    def test_use_top_parent_true(self):
        parent = DummyValidator(recursiveAnchor=True)
        # immediate parent is ignored
        validator = DummyValidator(parent=parent, recursiveAnchor=False)
        recursiveRef = RecursiveRef(
            schema={"$recursiveRef": "#"}, location="", parent=validator
        )

        recursiveRef.resolve()

        self.assertEqual(recursiveRef._validator, parent)

    def test_immediate_parent_is_ignored_true(self):
        parent = DummyValidator(recursiveAnchor=True)
        # immediate parent is ignored
        validator = DummyValidator(parent=parent, recursiveAnchor=True)
        recursiveRef = RecursiveRef(
            schema={"$recursiveRef": "#"}, location="", parent=validator
        )

        recursiveRef.resolve()

        self.assertEqual(recursiveRef._validator, parent)

    def test_immediate_parent_is_ignored_false(self):
        parent = DummyValidator(recursiveAnchor=True)
        # immediate parent is ignored
        validator = DummyValidator(parent=parent, recursiveAnchor=False)
        recursiveRef = RecursiveRef(
            schema={"$recursiveRef": "#"}, location="", parent=validator
        )

        recursiveRef.resolve()

        self.assertEqual(recursiveRef._validator, parent)

    def test_recursive_anchor_true_at_root(self):
        parent = DummyValidator(recursiveAnchor=True)
        validator = DummyValidator(parent=parent, recursiveAnchor=True)
        recursiveRef = RecursiveRef(
            schema={"$recursiveRef": "#"}, location="", parent=validator
        )

        recursiveRef.resolve()

        self.assertEqual(recursiveRef._validator, parent)
        recursiveRef(True, location="")

    def test_resolve_before_validator_resolved(self):
        parent = DummyValidator(recursiveAnchor=True)
        validator = DummyValidator(parent=parent, recursiveAnchor=True)
        recursiveRef = RecursiveRef(
            schema={"$recursiveRef": "#"}, location="", parent=validator
        )

        with self.assertRaises(ProgrammerError):
            recursiveRef(True, location="")
