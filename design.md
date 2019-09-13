## Design

### Notes from the spec
New media type  -> "application/schema+json" -> identifies a json schema
                -> "application/schema-instance+json" -> additional integration features

`Json schema` is defined over Json documents
A `Json document` to which a schema is applied is called an `instance`

Json instance has 6 primitive types
* `null`
* `boolean`
* `number` - base 10 decimal
* `string` - unicode code points
* `array`
* `object`


Instance Equality
* both are null; or
* both are true; or
* both are false; or
* both are strings, and are the same codepoint-for-codepoint; or
* both are numbers, and have the same mathematical value; or
* both are arrays, and have an equal value item-for-item; or
* both are objects, and each property in one has exactly one property with a key equal to the other's, and that other property has an equal value.
Same as equality in python

The "application/schema+json" media type is defined to offer a superset of the media type parameter and fragment identifier syntax and semantics provided by "application/schema-instance+json"


# Rules of the JsonSchema
A JSON Schema MUST be an object or a boolean
Object properties that are applied to the instance are called `keywords`
Two kinds - assertions or annotations
`Vocabulary` set of keywords for a defined purpose


`Root schema` and `subschemas`

`fragment identifier` -> two possible ones
* plain names
* `JSON pointers`



#### Concerns so far
JSON schema
JSON document
Vocabulary
Types
Keywords -> register a keyword as being for a given type and vocabulary
    $schema -> only applies to the root schema
    $id -> root schema should contain this with an absolute URI
Need a way to resolve references
Root schema
fragment identifier

"$schema" keyword
    - this is an annotation
    - schema version identifier and location of the resource - value needs to be a URI (containing a scheme)
    - should be used in a root schema
`$id` keyword - annotation too
    - URI for the schema
    - root schema should contain an "$id" keyword with an absolute-URI (scheme but no fragment or empty fragment)

Need to understand how Json Pointers are used in schemas - have this be a ticket for later



## Need to scope the work for this - WHat's tickets do I need to create to get this done?
* Read and understand https://json-schema.org/latest/json-schema-core.html + make notes
* Read and understand http://json-schema.org/latest/json-schema-validation.html + make notes
* Design a solution based on my notes - make architectural decisions
* Breakdown into smaller tasks like
    - support strings - string keywords and be able to write a schema that validates a string
    - support numbers - ^ all the stuff above
    - support boolean - ^ all the stuff above
    - support null - ^ all the stuff above
    - support arrays - array keywords. be able to write schema that validates an array
    - support objects - object keywords
* Support references
* Support comments

I can see myself doing this halfway too instead of implementing the entire spec. Good thing or bad thing to be always doing this?
