import json
import os
import typing as t
import unittest

import parameterized

from pyjschema.draft_2019_09 import validate_once

STRING_KEYWORDS = [
    "minLength",
    "maxLength",
    "pattern",
    "type",
    "format",  # not implemented anything here but it passes the tests
]

OBJECT_KEYWORDS = [
    "maxProperties",
    "minProperties",
    "properties",
    "propertyNames",
    "patternProperties",
    "additionalProperties",
    "required",
]

ARRAY_KEYWORDS = [
    "items",
    "uniqueItems",
    "minItems",
    "maxItems",
    "additionalItems",
    "contains",
]

NUMBER_KEYWORDS = [
    "maximum",
    "exclusiveMaximum",
    "minimum",
    "exclusiveMinimum",
    "multipleOf",
]

BOOLEAN_KEYWORDS = ["if-then-else", "anyOf", "oneOf", "allOf", "not"]
KEYWORDS = (
    STRING_KEYWORDS
    + NUMBER_KEYWORDS
    + BOOLEAN_KEYWORDS
    + ARRAY_KEYWORDS
    + OBJECT_KEYWORDS
    + [
        "anchor",  # need to support non-canonical URIs - support relate pointers in $id
        # "defs", # needs "https://json-schema.org/draft/2019-09/schema" in the ref
        "const",
        "enum",
        "boolean_schema",
        "default",
        "ref",  # need root ref - #, also escaped json-pointers,
        # "refRemote",
    ]
)


CWD = os.path.dirname(__file__)

KEYWORD_TESTS: t.List = []
for keyword in KEYWORDS:
    with open(
        os.path.join(CWD, f"json-schema-tests/tests/draft2019-09/{keyword}.json")
    ) as file:
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
