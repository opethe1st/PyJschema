import timeit
from textwrap import dedent

# apt-get install jsonschema json-spec validictory
import fastjsonschema
import jsonschema
from jsonspec.validators import load

import jschema
import jschema.draft_2019_09 as draft_1909
from jschema.draft_2019_09.validator_construction import construct_validator
from temp.performance import validate

NUMBER = 1000

JSON_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'type': 'array',
    'items': [
        {
            'type': 'number',
            'maximum': 10,
            'exclusiveMaximum': True,
        },
        {
            'type': 'string',
            'enum': ['hello', 'world'],
        },
        {
            'type': 'array',
            'minItems': 1,
            'maxItems': 3,
            'items': [
                {'type': 'number'},
                {'type': 'string', 'maxLength': 1000, 'pattern': '[a-z]*'},
                {'type': 'boolean'},
            ],
        },
        {
            'type': 'object',
            'required': ['a', 'b'],
            'minProperties': 3,
            'properties': {
                'a': {'type': ['null', 'string']},
                'b': {'type': ['null', 'string']},
                'c': {'type': ['null', 'string'], 'default': 'abc'}
            },
            'additionalProperties': {'type': 'string'},
        },
        {'not': {'type': ['null']}},
        {'oneOf': [
            {'type': 'number', 'multipleOf': 3},
            {'type': 'number', 'multipleOf': 5},
        ]},
    ],
}

VALUES_OK = (
    [9, 'hello', [1, 'a', True], {'a': 'a', 'b': 'b', 'd': 'd'}, 42, 3],
    [9, 'world', [1, 'a', True], {'a': 'a', 'b': 'b', 'd': 'd'}, 42, 3],
    [9, 'world', [1, 'a', True], {'a': 'a', 'b': 'b', 'c': 'xy'}, 42, 3],
    [9, 'world', [1, 'a', True], {'a': 'a', 'b': 'b', 'c': 'xy'}, 'str', 5],
)

VALUES_BAD = (
    [10, 'world', [1, 'a', True], {'a': 'a', 'b': 'b', 'c': 'xy'}, 'str', 5],
    [9, 'xxx', [1, 'a', True], {'a': 'a', 'b': 'b', 'c': 'xy'}, 'str', 5],
    [9, 'hello', [], {'a': 'a', 'b': 'b', 'c': 'xy'}, 'str', 5],
    [9, 'hello', [1, 2, 3], {'a': 'a', 'b': 'b', 'c': 'xy'}, 'str', 5],
    [9, 'hello', [1, 'a', True], {'a': 'a', 'x': 'x', 'y': 'y'}, 'str', 5],
    [9, 'hello', [1, 'a', True], {}, 'str', 5],
    [9, 'hello', [1, 'a', True], {'a': 'a', 'b': 'b', 'x': 'x'}, None, 5],
    [9, 'hello', [1, 'a', True], {'a': 'a', 'b': 'b', 'x': 'x'}, 42, 15],
)


fastjsonschema_validate = fastjsonschema.compile(JSON_SCHEMA)
fast_compiled = lambda value, _: fastjsonschema_validate(value)

fast_not_compiled = lambda value, json_schema: fastjsonschema.compile(json_schema)(value)

my_jsonschema = lambda value, json_schema: draft_1909.validate_once(schema=json_schema, instance=value)
validator = construct_validator(schema=JSON_SCHEMA)
# my_jsonschema_compiled = lambda value, _: validator.validate(instance=value)
def my_jsonschema_compiled(value, _):
    try:
        validator.validate(instance=value)
    except Exception:
        return False

with open('temp/performance.py', 'w') as f:
    f.write(fastjsonschema.compile_to_code(JSON_SCHEMA))
fast_file = lambda value, _: validate(value)

jsonspec = load(JSON_SCHEMA)


def t(func, valid_values=True):
    module = func.split('.')[0]

    setup = """from __main__ import (
        JSON_SCHEMA,
        VALUES_OK,
        VALUES_BAD,
        jschema,
        jsonschema,
        jsonspec,
        fast_compiled,
        fast_file,
        fast_not_compiled,
        my_jsonschema,
        my_jsonschema_compiled,
    )
    """

    if valid_values:
        code = dedent("""
        for value in VALUES_OK:
            {}(value, JSON_SCHEMA)
        """.format(func))
    else:
        code = dedent("""
        try:
            for value in VALUES_BAD:
                {}(value, JSON_SCHEMA)
        except:
            pass
        """.format(func))

    res = timeit.timeit(code, setup, number=NUMBER)
    print('{:<20} {:<10} ==> {}'.format(module, 'valid' if valid_values else 'invalid', res))


print('Number: {}'.format(NUMBER))

t('fast_compiled')
t('fast_compiled', valid_values=False)

t('fast_file')
t('fast_file', valid_values=False)

t('fast_not_compiled')
t('fast_not_compiled', valid_values=False)

t('jsonschema.validate')
t('jsonschema.validate', valid_values=False)


t('my_jsonschema')
t('my_jsonschema', valid_values=False)
t('my_jsonschema_compiled')
t('my_jsonschema_compiled', valid_values=False)
