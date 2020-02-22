import cProfile
import io
import pstats

# from jsonschema import Draft4Validator

from performance.large_schema import SCHEMA
from pyjschema.draft_2019_09 import construct_validator


INSTANCE = [9, "hello", [1, "a", True], {"a": "a", "b": "b", "d": "d"}, 42, 3]


if __name__ == "__main__":
    pr = cProfile.Profile()
    validator = construct_validator(SCHEMA)
    # validator = Draft4Validator(SCHEMA)
    pr.enable()
    for _ in range(10000):
        res = validator.validate(INSTANCE)
        # print(res)
    pr.disable()

    s = io.StringIO()
    sortby = 2
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(20)
    print(s.getvalue())
