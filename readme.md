# PyJSchema

An implementation of the JSON Schema specification

This currently only supports the [latest](https://json-schema.org/specification.html) json-schema draft except for the
`$recursiveAnchor` and `$recursiveRef` keywords and this passes most of the tests [in the official test suite](https://github.com/json-schema-org/JSON-Schema-Test-Suite)
(I modified one or two because the test suite hasn't been updated for draft_2019_09)

This is NOT intended to be used in production yet (Error message is currently not good enough and I don't know that I want to commit to maintaining this long term)
but if I get enough good feedback I might reconsider 😁.

## How to use

You should use `validate_once` when you are using a schema just once.
e.g
```python
from jsonschema.draft_2019_09 import validate_once

# result is ValidationError or True
result = validate_once(schema=True, instance="an instance")
```

If you are going to be using the same schema to validate different instances. You should construct a validator from the schema and then reuse that validator to validate the instances.
e.g

```python
from jsonschema.draft_2019_09 import construct_validator

validator = construct_validator(schema=True)

for instance in [True, 1234, {"key": "value"}, "string", ["abc"]]:
    result = validator.validate(instance="an instance")

```

This is similar to compiling regex and you can get significant speed improvements by compiling schemas that are used often


## Benchmarks
Pyjschema is pretty fast

![compile+run](/compile-run-benchmark.png)


![run](/run-benchmark.png)

Compared to the python jsonschema library it is some multiplies faster (at least 8). Compared to fastjsonschema it is faster when not compiled. And for the compiled case, it is like 75 percent slower.

Keep in mind that fastjsonschema makes use of Exceptions to indicate validation errors and this is the reason it is faster
(I created a [branch](https://github.com/opethe1st/PyJschema/tree/raise-exceptions-instead-of-returns) to test this assumption. You can run perf.py in that branch. The only change from my original code was that I raised Exceptions instead of trying to return ValidationErrors. This made my code even faster than fastjsonschema).
You can't generate a list of all the validation errors when you use exceptions that way. That's an important feature so I accept the speed penalty for supporting listing all the errors that occur :D

## Feedback?
You can tweet at me at @opeispo. Did you find this code easy to read and understand? What would you do differently? Liked the approach?
