import json
import unittest

from jsonschema.draft_2019_09 import validate_once
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
        # "propertyNames",
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

    ])
    def tests(self, keyword):
        with open(f"tests/json-schema-tests/tests/draft2019-09/{keyword}.json") as file:
            tests = json.load(file)

        for data in tests:
            schema = data["schema"]
            for test in data["tests"]:
                with self.subTest(test["description"]):
                    self.assertEqual(
                        validate_once(schema, instance=test["data"]).ok,
                        test["valid"]
                    )
