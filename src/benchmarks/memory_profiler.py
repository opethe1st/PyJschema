import fastjsonschema
import jsonschema
from memory_profiler import profile

from jschema.draft_2019_09 import construct_validator

SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "array",
    "items": [
        {"type": "number", "maximum": 10, "exclusiveMaximum": True},
        {"type": "string", "enum": ["hello", "world"]},
        {
            "type": "array",
            "minItems": 1,
            "maxItems": 3,
            "items": [
                {"type": "number"},
                {"type": "string", "maxLength": 1000, "pattern": "[a-z]*"},
                {"type": "boolean"},
            ],
        },
        {
            "type": "object",
            "required": ["a", "b"],
            "minProperties": 3,
            "properties": {
                "a": {"type": ["null", "string"]},
                "b": {"type": ["null", "string"]},
                "c": {"type": ["null", "string"], "default": "abc"},
            },
            "additionalProperties": {"type": "string"},
        },
        {"not": {"type": ["null"]}},
        {
            "oneOf": [
                {"type": "number", "multipleOf": 3},
                {"type": "number", "multipleOf": 5},
            ]
        },
    ],
}
INSTANCE = [9, "hello", [1, "a", True], {"a": "a", "b": "b", "d": "d"}, 42, 3]


@profile
def mem_profile_pyjschema():
    validator = construct_validator(schema=SCHEMA)
    validator.validate(INSTANCE)


@profile
def mem_profile_jsonchema():
    js_validator = jsonschema.Draft4Validator(schema=SCHEMA)
    js_validator.validate(INSTANCE)


@profile
def mem_profile_fastjsonchema():
    fastvalidator = fastjsonschema.compile(SCHEMA)
    fastvalidator(INSTANCE)


if __name__ == "__main__":
    mem_profile_pyjschema()
    mem_profile_jsonchema()
    mem_profile_fastjsonchema()
