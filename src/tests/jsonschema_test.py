import json
import unittest

from jschema.draft_2019_09 import validate_once
import parameterized


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

        # "anchor",

        # "defs",

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

        # "anyOf",
        # "oneOf",
        # "allOf",
        # "dependencies", # is this still a thing in draft2019-09
        # "default",
        # "format",
        # "not",
        # "ref",
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
