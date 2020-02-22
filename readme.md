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


## Feedback?
You can tweet at me at @opeispo. Did you find this code easy to read and understand? What would you do differently? Liked the approach?
