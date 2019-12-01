# PyJSchema

An implementation of the JSON Schema specification

This currently only supports the [latest](https://json-schema.org/specification.html) json-schema specification except for a couple of keywords e.g `$recursiveAnchor`, `$recursiveRef`, `unevaluatedProperties` etc
It passes most of the tests [in the official test suite](https://github.com/json-schema-org/JSON-Schema-Test-Suite)
(I modified/remove one or two tests because the test suite hasn't been updated for draft_2019_09)

This is NOT intended to be used in production yet because it is still rough around the edges. (Error messages are currently not good enough and I don't know that I want to commit to maintaining this long term)
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

![compile+run](/images/compile-run-benchmark.png)


![run](/images/run-benchmark.png)

Compared to the python jsonschema library it is some multiplies faster (at least 8). Compared to fastjsonschema it is faster when the validator is compiled everytime validation happens. If the validator is compiled and then reused then it is like 75 percent slower.

Keep in mind that fastjsonschema makes use of Exceptions to indicate validation errors and this is the reason it is faster
(I created a [branch](https://github.com/opethe1st/PyJschema/compare/raise-exceptions-instead-of-returns) to test this assumption. You can run perf.py in that branch and see that this library is faster. The code change was raising Exceptions.
You can't generate a list of all the validation errors when you use exceptions that way. That's an important feature so I accept the speed penalty for supporting listing all the errors that occur 😄

## Feedback?
You can tweet at me at @opeispo. Did you find this code easy to read and understand? What would you do differently? Liked the approach?
