import typing as t

from .validation_result import ValidationResult
from .validator import AValidator, Keyword

Context = t.Dict[str, AValidator]


def generate_context(validator: AValidator) -> Context:
    uri_to_validator: Context = {}

    if validator.anchor is not None:
        uri_to_validator[validator.id + validator.anchor] = validator

    # This supports just canonical URIs
    if validator.id is not None:
        uri_to_validator[validator.id] = validator

    for sub_validator in validator.subschema_validators():
        sub_uri_to_validator = generate_context(validator=sub_validator)
        uri_to_validator.update(sub_uri_to_validator)

    return uri_to_validator


def attach_base_URIs(validator: AValidator, parent_URI):
    if validator.id is None:
        validator.id = parent_URI

    for sub_validator in validator.subschema_validators():
        attach_base_URIs(
            validator=sub_validator, parent_URI=validator.id
        )


def add_context_to_ref_validators(validator: t.Union[AValidator], context: Context):
    if isinstance(validator, Ref):
        validator.set_context(context)

    for sub_validators in validator.subschema_validators():
        add_context_to_ref_validators(validator=sub_validators, context=context)


class Ref(Keyword):
    def __init__(self, ref):
        self.value = ref
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
