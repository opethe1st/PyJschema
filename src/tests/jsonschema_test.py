import json
import typing as t
import unittest

import parameterized

from pyjschema.draft_2019_09 import validate_once

KEYWORDS = [
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
    "anchor",  # need to support non-canonical URIs - support relate pointers in $id
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
    "ref",  # need root ref - #, also escaped json-pointers,
    # $ref not a reference, references that are not json pointer but relative
    # to current base URI
    # "refRemote",
]


KEYWORD_TESTS: t.List = []
for keyword in KEYWORDS:
    with open(f"tests/json-schema-tests/tests/draft2019-09/{keyword}.json") as file:
        keyword_testcases = json.load(file)
        for testcase in keyword_testcases:
            testcase["keyword"] = keyword

    KEYWORD_TESTS.extend(keyword_testcases)


class Test(unittest.TestCase):
    @parameterized.parameterized.expand(
        [(test["keyword"] + test["description"], test) for test in KEYWORD_TESTS]
    )
    def tests(self, description, testcase):
        schema = testcase["schema"]
        for test in testcase["tests"]:
            with self.subTest(test["description"]):
                self.assertEqual(
                    bool(validate_once(schema, instance=test["data"])), test["valid"]
                )
