import unittest

from .ref import Ref, RecursiveRef
from .validator import Validator


class DummyValidator(Validator):
    def __init__(self, parent=None, recursiveAnchor=False):
        self.parent = parent
        self.recursiveAnchor = recursiveAnchor


class TestRefResolve(unittest.TestCase):
    def test(self):
        ref = Ref(schema={"$ref": "other.json"})
        ref.base_uri = "https://localhost:5000/root.json"
        validator = DummyValidator()

        ref.resolve(uri_to_validator={"https://localhost:5000/other.json": validator})

        self.assertEqual(ref._validator, validator)


class TestRecursiveRef(unittest.TestCase):
    def test_is_root(self):
        validator = DummyValidator()
        recursiveRef = RecursiveRef(schema={"$recursiveRef": "#"}, parent=validator)

        recursiveRef.resolve()

        self.assertEqual(recursiveRef._validator, validator)

    def test_is_not_root(self):
        parent = DummyValidator()
        validator = DummyValidator(parent=parent, recursiveAnchor=False)
        recursiveRef = RecursiveRef(schema={"$recursiveRef": "#"}, parent=validator)

        recursiveRef.resolve()

        self.assertEqual(recursiveRef._validator, validator)

    def test_is_recursive_ref_true(self):
        parent = DummyValidator()
        validator = DummyValidator(parent=parent, recursiveAnchor=True)
        recursiveRef = RecursiveRef(schema={"$recursiveRef": "#"}, parent=validator)

        recursiveRef.resolve()

        self.assertEqual(recursiveRef._validator, parent)

    def test_recursive_anchor_true_at_root(self):
        parent = DummyValidator(recursiveAnchor=True)
        validator = DummyValidator(parent=parent, recursiveAnchor=True)
        recursiveRef = RecursiveRef(schema={"$recursiveRef": "#"}, parent=validator)

        recursiveRef.resolve()

        self.assertEqual(recursiveRef._validator, parent)
