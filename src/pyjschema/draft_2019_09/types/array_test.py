import unittest

from pyjschema.draft_2019_09 import construct_validator


class Test(unittest.TestCase):
    def test(self):
        instance = [
            [{"foo": None}, {"foo": None}, {"foo": None}],
        ]
        schema = {
            "$defs": {
                "item": {
                    "type": "array",
                    "additionalItems": False,
                    "items": [
                        {"$ref": "#/$defs/sub-item"},
                        {"$ref": "#/$defs/sub-item"},
                    ],
                },
                "sub-item": {"type": "object", "required": ["foo"]},
            },
            "type": "array",
            "additionalItems": False,
            "items": [{"$ref": "#/$defs/item"},],
        }

        validator = construct_validator(schema=schema)
        self.assertEqual(bool(validator(instance)), False)
