import typing as t

from jsonschema.common import ValidationResult

from .validator import AValidator, Keyword

Context = t.Dict[str, AValidator]


class Ref(Keyword):
    def __init__(self, ref):
        self.value = ref.value
        self.context: t.Optional[Context] = None

    def validate(self, instance):
        if self.context is None:
            # Maybe have another state for not validated?
            return ValidationResult(ok=True)
        if self.value in self.context:
            return self.context[self.value].validate(instance)
        else:
            # this is temporary, probably need to do something else
            raise Exception(f"unable to find this reference. reference {self.value}")
        return ValidationResult(ok=True)

    def set_context(self, context):
        self.context = context

    def __eq__(self, other) -> bool:
        if not isinstance(other, Ref):
            return NotImplemented
        return self.value == other.value
