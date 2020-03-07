import numbers

from pyjschema.common import Keyword
from pyjschema.utils import ValidationResult

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

    def __init__(self, schema, location, parent):
        super().__init__(schema=schema, location=location, parent=parent)
        types = schema.get("type")
        if isinstance(types, str):
            types = [schema["type"]]
        self._types = types

    def __call__(self, instance, location=None):
        for type_ in self._types:
            if isinstance_(instance, NAME_TO_TYPE[type_]):
                return True
        return ValidationResult(
            message=f"{instance!r} is not a {self.value}",
            location=location,
            keywordLocation=self.location,
        )

    def __repr__(self):
        return f"Type({self._types})"


def isinstance_(obj, type_):
    if type_ in (int, numbers.Number) and isinstance(obj, bool):
        return False
    return isinstance(obj, type_)
