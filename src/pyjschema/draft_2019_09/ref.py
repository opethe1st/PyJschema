from functools import wraps

from uritools import uridecode

from pyjschema.common import Keyword

from .exceptions import SchemaError
from .utils import to_canonical_uri


def raise_if_not_ready(func):
    @wraps(func)
    def wrapper(self, *arg, **kwargs):
        if not self.is_resolved:
            raise Exception(
                "You are trying to call a method on a reference that is not resolved. Call the resolve method"
            )
        return func(self, *arg, **kwargs)

    return wrapper


class Ref(Keyword):
    keyword = "$ref"

    def __init__(self, schema):
        super().__init__(schema=schema)
        self.value = uridecode(self.value.replace("~1", "/").replace("~0", "~"))
        self._validator = None
        self.abs_uri = None

    @property
    def is_resolved(self):
        return all([self.abs_uri is not None, self._validator is not None])

    @raise_if_not_ready
    def validate(self, instance):
        return self._validator.validate(instance)

    def resolve(self, uri_to_validator):
        self.abs_uri = self._get_abs_uri()
        self._validator = self._get_validator(uri_to_validator=uri_to_validator)

    def _get_abs_uri(self):
        # needs to be called after self.base)uri has been set to canonical form
        if self.value == '#':
            return self.value
        return to_canonical_uri(uri=self.value, current_base_uri=self.base_uri or '')

    def _get_validator(self, uri_to_validator):
        # test this?
        validator = uri_to_validator.get(self.abs_uri)

        if validator:
            return validator
        else:
            # TODO(ope): better error message
            raise SchemaError(
                f"Unable to locate the validator "
                f"while trying to resolve this reference: {self.value!r} at {self.location} "
                f"{list(uri_to_validator.keys())}"
            )

    def __repr__(self):
        return f"Ref(value={self.abs_uri!r})"


class RecursiveRef(Keyword):

    keyword = "$recursiveRef"

    def __init__(self, schema, parent=None):
        super().__init__(schema=schema, parent=parent)
        self.value = uridecode(self.value.replace("~1", "/").replace("~0", "~"))
        self._validator = None
        self.abs_uri = None
        self.is_resolved = False

    def resolve(self):
        from .validator import Validator

        validator = self
        while validator.parent is not None:
            if isinstance(validator, Validator) and validator.recursiveAnchor is False:
                break
            validator = validator.parent

        self._validator = validator
        self.is_resolved = True

    @raise_if_not_ready
    def validate(self, instance):
        return self._validator.validate(instance)

    def __repr__(self):
        return "RecursiveRef()"
