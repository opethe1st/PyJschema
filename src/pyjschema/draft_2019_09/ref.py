from functools import wraps

from uritools import uridecode

from pyjschema.common import Keyword
from pyjschema.exceptions import ProgrammerError, SchemaError

from pyjschema.utils import to_canonical_uri, basic_output


def raise_if_not_ready(func):
    @wraps(func)
    def wrapper(self, *arg, **kwargs):
        if not self.is_resolved:
            raise ProgrammerError(
                "You are trying to call a method on a reference that is not resolved. Call the resolve method"
            )
        return func(self, *arg, **kwargs)

    return wrapper


class Ref(Keyword):
    keyword = "$ref"

    def __init__(self, schema, location, parent):
        super().__init__(schema=schema, location=location, parent=parent)
        self.value = uridecode(self.value.replace("~1", "/").replace("~0", "~"))
        self._validator = None
        self.abs_uri = None

    @property
    def is_resolved(self):
        return all([self.abs_uri is not None, self._validator is not None])

    @basic_output("failed recursiveRef")
    @raise_if_not_ready
    def __call__(self, instance, location=None):
        return self._validator(instance=instance, location=location)

    def resolve(self, uri_to_validator):
        abs_uri = self._get_abs_uri()
        self.abs_uri = abs_uri
        self._validator = self._get_validator(
            abs_uri=abs_uri, uri_to_validator=uri_to_validator
        )

    def _get_abs_uri(self):
        if self.base_uri is None:
            raise ProgrammerError("base_uri cannot be None")
        if self.value == "#":
            return self.value
        return to_canonical_uri(uri=self.value, current_base_uri=self.base_uri or "")

    def _get_validator(self, abs_uri, uri_to_validator):
        validator = uri_to_validator.get(abs_uri)

        if validator:
            return validator
        else:
            raise SchemaError(
                f"Unable to locate the validator "
                f"while trying to resolve this reference: {self.value!r} at {self.location} "
                f"{list(uri_to_validator.keys())}"
            )

    def __repr__(self):
        return f"Ref(value={self.abs_uri!r})"


class RecursiveRef(Keyword):

    keyword = "$recursiveRef"

    def __init__(self, schema, location, parent):
        super().__init__(schema=schema, location=location, parent=parent)
        self.value = uridecode(self.value.replace("~1", "/").replace("~0", "~"))
        self._validator = None
        self.abs_uri = None

    @property
    def is_resolved(self):
        return all([self._validator is not None])

    def resolve(self):
        from .validator import Validator

        validator = self.parent.parent
        parent_validator = self.parent
        while validator:
            if isinstance(validator, Validator) and validator.recursiveAnchor is False:
                break
            parent_validator = validator
            validator = validator.parent

        self._validator = parent_validator

    @basic_output("failed recursiveRef")
    @raise_if_not_ready
    def __call__(self, instance, location=None):
        return self._validator(instance=instance, location=location)

    def __repr__(self):
        return f"RecursiveRef({self._validator})"
