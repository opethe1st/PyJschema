import unittest

from .ref import Ref


class DummyRef(Ref):
    def __init__(self):
        self.value = None
        self._validator = None


class DummyValidator:
    pass


class TestRefResolve(unittest.TestCase):

    def test(self):
        ref = DummyRef()
        ref.base_uri = "https://localhost:5000/root.json"
        ref.value = "other.json"
        validator = DummyValidator()

        ref.resolve(uri_to_validator={"https://localhost:5000/other.json": validator})

        self.assertEqual(ref._validator, validator)
