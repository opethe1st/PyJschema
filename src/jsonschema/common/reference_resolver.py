import typing as t

from .validation_result import ValidationResult
from .validator import AValidator, Keyword

Context = t.Dict[str, AValidator]


def generate_context(validator: AValidator) -> Context:
    anchors = {}
    # I might be able to do without this check if I restrict that this is allowed to pass in to just Validator
    if hasattr(validator, "anchor") and validator.anchor is not None:  # type: ignore
        anchors[validator.anchor] = validator  # type: ignore
    for sub_validator in validator.subschema_validators():
        subanchor = generate_context(validator=sub_validator)
        anchors.update(subanchor)
    return anchors


def add_context_to_ref_validators(validator: t.Union[AValidator], context: Context):
    if isinstance(validator, Ref):
        validator.set_context(context)

    for sub_validators in validator.subschema_validators():
        add_context_to_ref_validators(validator=sub_validators, context=context)


class Ref(Keyword):
    def __init__(self, value):
        self.value = value
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
