from functools import partial

import fastjsonschema
import jsonschema
import pytest

from benchmarks.large_schema import SCHEMA
from pyjschema.draft_2019_09 import construct_validator, validate_once

INSTANCE = [9, "hello", [1, "a", True], {"a": "a", "b": "b", "d": "d"}, 42, 3]


@pytest.mark.benchmark(group="compile+run", min_time=0.1, max_time=0.5, min_rounds=5)
def test_pyjschema(benchmark):
    def validate_pyjschema():
        validate_once(SCHEMA, INSTANCE)

    benchmark(validate_pyjschema)


@pytest.mark.benchmark(group="compile+run", min_time=0.1, max_time=0.5, min_rounds=5)
def test_jsonschema(benchmark):
    def validate_jsonschema():
        jsonschema.validate(schema=SCHEMA, instance=INSTANCE)

    benchmark(validate_jsonschema)


@pytest.mark.benchmark(group="compile+run", min_time=0.1, max_time=0.5, min_rounds=5)
def test_fastjsonschema(benchmark):
    def validate_fastjsonschema():
        fastjsonschema.compile(SCHEMA)(INSTANCE)

    benchmark(validate_fastjsonschema)


@pytest.mark.benchmark(group="run", min_time=0.1, max_time=0.5, min_rounds=5)
def test_pyjschema_compiled(benchmark):
    pyjschema_validate_func = construct_validator(SCHEMA).validate
    benchmark(partial(pyjschema_validate_func, INSTANCE))


@pytest.mark.benchmark(group="run", min_time=0.1, max_time=0.5, min_rounds=5)
def test_jsonschema_compiled(benchmark):
    jsonschema_validate_func = jsonschema.Draft4Validator(SCHEMA).validate
    benchmark(partial(jsonschema_validate_func, instance=INSTANCE))


@pytest.mark.benchmark(group="run", min_time=0.1, max_time=0.5, min_rounds=5)
def test_fastjsonschema_compiled(benchmark):
    fastjsonschema_validate_func = fastjsonschema.compile(SCHEMA)
    benchmark(partial(fastjsonschema_validate_func, INSTANCE))
