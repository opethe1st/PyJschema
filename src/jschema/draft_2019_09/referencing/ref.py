import re
import typing as t
from urllib import parse

from jschema.common import AValidator, Keyword, ValidationResult

Context = t.Dict[str, AValidator]


FRAGMENT_REGEX = re.compile(pattern=r"#.*")
BASE_URI_REGEX = re.compile(pattern=r"http.*")


class Ref(Keyword):
    def __init__(self, schema):
        ref = schema.value["$ref"]
        value = ref.value.replace("~1", "/")
        value = value.replace("~0", "~")
        self.value = parse.unquote(value)
        self.context: t.Optional[Context] = None

    def validate(self, instance):
        if self.context is None:
            # Maybe have another state for not validated?
            return ValidationResult(ok=True)

        # looks like this needs a resolver function here
        value = self.value
        if FRAGMENT_REGEX.match(value):
            value = self.id + value

        if not BASE_URI_REGEX.match(value):
            parts = self.id.split("/")
            parts[-1] = value
            value = "/".join(parts)

        validator = self._resolve_uri(uri=value)

        if validator:
            return validator.validate(instance)
        else:
            # this is temporary, probably need to do something else
            raise Exception(
                f"unable to find this reference '{value}' in valid_references: {self.context.keys()}"
            )

    def set_context(self, context):
        self.context = context

    def set_base_uri_to_abs_location(self, base_uri_to_abs_location):
        self.base_uri_to_abs_location = base_uri_to_abs_location

    def _resolve_uri(self, uri):
        return resolve_uri(
            uri=uri,
            context=self.context,
            base_uri_to_abs_location=self.base_uri_to_abs_location,
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Ref):
            return NotImplemented
        return self.value == other.value


# TODO(ope): need to fix this
BASE_URI_AND_ANCHOR_REGEX = re.compile(pattern=r"http.*#[a-zA-Z].*")


# TODO(ope): this needs to be refactored a lot!!
def resolve_uri(context, uri, base_uri_to_abs_location):
    if uri in context:
        return context[uri]
    if BASE_URI_AND_ANCHOR_REGEX.match(uri):
        return context[uri]
    base_uri, fragment = uri.split("#") if ("#" in uri and uri != "#") else [uri, ""]
    if (base_uri and not fragment) or (not base_uri and fragment):
        if base_uri:
            return context[base_uri]
        else:
            return context["#" + fragment]
    else:
        if base_uri in base_uri_to_abs_location:
            uri_location = base_uri_to_abs_location[base_uri]
            return context[f"{uri_location}{fragment}"]
        else:
            return context[f"#{fragment}"]
