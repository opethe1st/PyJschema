import unittest

import parameterized  # type: ignore

from pyjschema.common.annotate import annotate
from pyjschema.draft_2019_09 import build_validator

from .referencing import _attach_base_URIs, _generate_context, _resolve_references


class TestAttachBaseURI(unittest.TestCase):
    @parameterized.parameterized.expand(
        [
            (
                "make sure that the expected base_URI are set 1",
                {"$id": "http://localhost:1234/root#"},
                {"http://localhost:1234/root", "http://localhost:1234/root#"},
            ),
            (
                "make sure that the expected base_URI are set",
                {
                    "$id": "http://localhost:1234/root",
                    "type": "array",
                    "items": {"$id": "items"},
                },
                {"http://localhost:1234/root", "items"},
            ),
            (
                "make sure that the expected base_URI are set 2",
                {
                    "$id": "http://localhost:1234/root.json#",
                    "type": "array",
                    "items": {"$id": "/items/abc.json"},
                },
                {
                    "http://localhost:1234/root.json",
                    "http://localhost:1234/root.json#",
                    "/items/abc.json",
                },
            ),
        ]
    )
    def test(self, description, schema, base_uris):
        validator = build_validator(schema=annotate(obj=schema))
        _attach_base_URIs(validator=validator, parent_URI=schema["$id"].rstrip("#"))
        self.assertEqual(get_base_uris(validator=validator), base_uris)


def get_base_uris(validator):
    uris = {validator.id} if validator.id else set()
    for subvalidator in validator.sub_validators():
        uris |= get_base_uris(subvalidator)
    return uris
