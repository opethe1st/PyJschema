import cProfile
import pstats
import timeit

import fastjsonschema
import jsonschema

from jschema.draft_2019_09 import construct_validator


if __name__ == "__main__":
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
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
    instance = [9, "hello", [1, "a", True], {"a": "a", "b": "b", "d": "d"}, 42, 3]

    for library, compile_statemnt, validate_statement, validate in [
        (
            "Jsonschema",
            "jsonschema.Draft4Validator(schema=schema)",
            "validate(instance=instance)",
            jsonschema.Draft4Validator(schema=schema).validate,
        ),
        (
            "Fastjsonschema",
            "fastjsonschema.compile(schema)",
            "validate(instance)",
            fastjsonschema.compile(schema),
        ),
        (
            "PyJschema",
            "construct_validator(schema)",
            "validate(instance=instance)",
            construct_validator(schema).validate,
        ),
    ]:
        print(library)
        print("-" * 20)

        compile_time = timeit.timeit(
            stmt=compile_statemnt, globals=globals(), number=100
        )
        print(f"compile time: {compile_time}")

        run_time = timeit.timeit(
            stmt=validate_statement, globals=globals(), number=10000
        )
        print(f"run time: {run_time}")
        print()

    for library, compile_statemnt, validate_statement, validate in [
        (
            "Jsonschema",
            "jsonschema.Draft4Validator(schema=schema)",
            "validate(instance=instance)",
            jsonschema.Draft4Validator(schema=schema).validate,
        ),
        (
            "Fastjsonschema",
            "fastjsonschema.compile(schema)",
            "validate(instance)",
            fastjsonschema.compile(schema),
        ),
        (
            "PyJschema",
            "construct_validator(schema)",
            "validate(instance=instance)",
            construct_validator(schema).validate,
        ),
    ]:
        profile = cProfile.Profile()
        profile.enable()
        validate(instance)
        profile.disable()

        print(library)
        stats = pstats.Stats(profile)
        stats.sort_stats("cumulative").print_stats()
