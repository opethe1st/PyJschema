import numbers

from pyjschema.common import AValidator, ValidationError

NAME_TO_TYPE = {
    "string": str,
    # boolean needs to be before integer and number
    "boolean": bool,
    "integer": int,
    "number": numbers.Number,
    "array": list,
    "object": dict,
    "null": type(None),
}


class Type(AValidator):
    """Validator for a type"""

    def __init__(self, schema, location=None):
        super().__init__(schema=schema, location=location)
        types = schema.get("type")
        if isinstance(types, str):
            types = [schema["type"]]
        self._types = types

    def validate(self, instance):
        messages = []
        for type_ in self._types:

            if isinstance_(instance, NAME_TO_TYPE[type_]):
                if isinstance(instance, dict):
                    if any(not isinstance(key, str) for key in instance):
                        messages.append(f"object needs to have string keys")
                        break
                return True
            else:
                messages.append(f"instance is not a {type_}")

        if messages:
            return ValidationError(messages=messages)
        return True


def isinstance_(obj, type_):
    if type_ in (int, numbers.Number) and isinstance(obj, bool):
        return False
    return isinstance(obj, type_)
