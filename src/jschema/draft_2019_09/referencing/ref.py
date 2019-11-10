import re
import typing as t
from urllib import parse

from jschema.common import AValidator, Keyword, ValidationResult

Context = t.Dict[str, AValidator]


FRAGMENT_REGEX = re.compile(pattern=r'#.*')
BASE_URI_REGEX = re.compile(pattern=r'http.*')


class Ref(Keyword):
    def __init__(self, schema):
        ref = schema.value["$ref"]
        value = ref.value.replace('~1', '/')
        value = value.replace('~0', '~')
        self.value = parse.unquote(value)
        self.context: t.Optional[Context] = None

    def validate(self, instance):
        if self.context is None:
            # Maybe have another state for not validated?
            return ValidationResult(ok=True)

        value = self.value
        if FRAGMENT_REGEX.match(value):
            value = self.id + value
        if not BASE_URI_REGEX.match(value):
            parts = self.id.split('/')
            parts[-1] = value
            value = "/".join(parts)
        if value in self.context:
            return self.context[value].validate(instance)
        else:
            # this is temporary, probably need to do something else
            raise Exception(f"unable to find this reference '{value}' in valid_references: {self.context.keys()}")
        return ValidationResult(ok=True)

    def set_context(self, context):
        self.context = context

    def __eq__(self, other) -> bool:
        if not isinstance(other, Ref):
            return NotImplemented
        return self.value == other.value
