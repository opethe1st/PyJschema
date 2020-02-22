import fastjsonschema
import jsonschema
from memory_profiler import profile

from pyjschema.draft_2019_09 import construct_validator

from performance.large_schema import SCHEMA

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
