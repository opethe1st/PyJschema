import json
import unittest

import parameterized

from jschema.draft_2019_09 import validate_once


class Test(unittest.TestCase):
    @parameterized.parameterized.expand([
        # string
        "minLength",
        "maxLength",
        "pattern",

        "type",

        # object
        "uniqueItems",
        "maxProperties",
        "minProperties",
        "properties",
        "propertyNames",
        "patternProperties",
        "additionalProperties",
        "uniqueItems",

        # "anchor",  # need to support non-canonical URIs - support relate pointers in $id

        # "defs", # needs "https://json-schema.org/draft/2019-09/schema" in the ref

        # array
        "items",
        "minItems",
        "maxItems",
        "additionalItems",
        "contains",

        # numbers
        "maximum",
        "exclusiveMaximum",
        "minimum",
        "exclusiveMinimum",
        "multipleOf",

        "const",

        "enum",

        "if-then-else",

        "boolean_schema",
        "required",

        "anyOf",
        "oneOf",
        "allOf",
        "default",
        "format",  # not implemented anything here but it passes the tests
        "not",
        # "ref",  # need root ref - #, also escaped json-pointers,
        # $ref not a reference, references that are not json pointer but relative
        # to current base URI
        # "refRemote",
    ])
    def tests(self, keyword):
        with open(f"src/tests/json-schema-tests/tests/draft2019-09/{keyword}.json") as file:
            tests = json.load(file)

        for data in tests:
            schema = data["schema"]
            for test in data["tests"]:
                with self.subTest(test["description"]):
                    self.assertEqual(
                        validate_once(schema, instance=test["data"]).ok,
                        test["valid"]
                    )
