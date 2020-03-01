import numbers

from pyjschema.common import Keyword
from pyjschema.utils import basic_output

NAME_TO_TYPE = {
    "string": str,
    "boolean": bool,
    "integer": int,
    "number": numbers.Number,
    "array": list,
    "object": dict,
    "null": type(None),
}


class Type(Keyword):
    """Validator for a type"""

    keyword = "type"

    def __init__(self, schema, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        types = schema.get("type")
        if isinstance(types, str):
            types = [schema["type"]]
        self._types = types

    @basic_output("{instance!r} is not of this type: {value!r}.")
    def __call__(self, instance, location=None):
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
            return False
        return True

    def __repr__(self):
        return f"Type({self._types})"


def isinstance_(obj, type_):
    if type_ in (int, numbers.Number) and isinstance(obj, bool):
        return False
    return isinstance(obj, type_)
