from functools import partial

import fastjsonschema
import jsonschema
import pytest

from jschema.draft_2019_09 import construct_validator, validate_once

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


@pytest.mark.benchmark(
    group="compile+run",
    min_time=0.1,
    max_time=0.5,
    min_rounds=5,
)
def test_pyjschema(benchmark):
    def validate_pyjschema():
        validate_once(SCHEMA, INSTANCE)
    benchmark(validate_pyjschema)


@pytest.mark.benchmark(
    group="compile+run",
    min_time=0.1,
    max_time=0.5,
    min_rounds=5,
)
def test_jsonschema(benchmark):
    def validate_jsonschema():
        jsonschema.validate(schema=SCHEMA, instance=INSTANCE)
    benchmark(validate_jsonschema)


@pytest.mark.benchmark(
    group="compile+run",
    min_time=0.1,
    max_time=0.5,
    min_rounds=5,
)
def test_fastjsonschema(benchmark):
    def validate_fastjsonschema():
        fastjsonschema.compile(SCHEMA)(INSTANCE)
    benchmark(validate_fastjsonschema)


@pytest.mark.benchmark(
    group="run",
    min_time=0.1,
    max_time=0.5,
    min_rounds=5,
)
def test_pyjschema_compiled(benchmark):
    pyjschema_validate_func = construct_validator(SCHEMA).validate
    benchmark(partial(pyjschema_validate_func, INSTANCE))


@pytest.mark.benchmark(
    group="run",
    min_time=0.1,
    max_time=0.5,
    min_rounds=5,
)
def test_jsonschema_compiled(benchmark):
    jsonschema_validate_func = jsonschema.Draft4Validator(SCHEMA).validate
    benchmark(partial(jsonschema_validate_func, instance=INSTANCE))


@pytest.mark.benchmark(
    group="run",
    min_time=0.1,
    max_time=0.5,
    min_rounds=5,
)
def test_fastjsonschema_compiled(benchmark):
    fastjsonschema_validate_func = fastjsonschema.compile(SCHEMA)
    benchmark(partial(fastjsonschema_validate_func, INSTANCE))
