from functools import wraps

from uritools import SplitResult, urijoin, urisplit

from pyjschema.common import KeywordGroup

from .exceptions import SchemaError


def raise_if_not_ready(func):
    @wraps(func)
    def wrapper(self, *arg, **kwargs):
        if not self.is_ready:
            raise Exception(
                "You are trying to call a method on an instance that is not ready. Call the preprare method"
            )
        return func(self, *arg, **kwargs)

    return wrapper


class Ref(KeywordGroup):
    def __init__(self, schema):
        super().__init__(schema=schema)
        self.value = schema["$ref"]
        self._validator = None
        self.rel_uri = None

    @property
    def is_ready(self):
        return all(self.rel_uri is not None, self._validator is not None)

    @raise_if_not_ready
    def validate(self, instance):
        return self._validator.validate(instance)

    def resolve(self, uri_to_validator, uri_to_root_location):
        self.rel_uri = self._to_rel_uri(uri_to_root_location=uri_to_root_location)
        self._validator = self._get_validator(uri_to_validator=uri_to_validator)

    def _to_rel_uri(self, uri_to_root_location):
        value: SplitResult = urisplit(self.value)
        has_authority = bool(value.scheme and value.authority)
        has_path = bool(value.path)
        has_fragment = bool(value.fragment)
        base_uri = self.base_uri.rstrip()

        if not has_authority and not has_path and has_fragment:
            if is_plain_name(value.fragment):
                return urijoin(base_uri + "#", value.fragment)
            elif is_json_pointer(value.fragment):
                # should make sure this is a valid json pointer
                # and also unquote
                return urijoin(base_uri, value.fragment)
        elif not has_authority and has_path and not has_fragment:
            return urijoin(base_uri.rstrip(), value.path)
        elif has_authority:
            if not has_path and not has_fragment:
                return self.value
            elif has_path and not has_fragment:
                # this should throw better than the index error
                root_location = urijoin(uri_to_root_location[""], uri_to_root_location[self.value])
                return urijoin(root_location, value.path)
            elif not has_path and has_fragment and is_json_pointer(value.fragment):
                if base_uri == uri_to_root_location[""]:
                    return urijoin(base_uri, value.fragment)
                else:
                    return urijoin(uri_to_root_location[self.value], value.fragment)

        raise SchemaError("Unable to resolve this uri")

    def _get_validator(self, uri_to_validator):
        validator = uri_to_validator.get(self.rel_uri)
        if validator:
            return validator
        else:
            raise SchemaError(
                f"Unable to locate the validator at this canonical URI: {self.canonical_uri}"
                "while trying to resolve this reference: {self.value} at {self.location}"
            )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Ref):
            return NotImplemented
        return self.value == other.value


def is_plain_name(val):
    return False


def is_json_pointer(val):
    return False
