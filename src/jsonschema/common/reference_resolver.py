import typing

from jsonschema.common.validator import AValidator

from .validation_result import ValidationResult

Context = typing.Dict[str, "AValidator"]


# TODO(ope): move these two to reference resolver
def generate_context(validator: "AValidator") -> Context:
    ids = {}
    # I might be able to do without this check if I restrict that this is allowed to pass in to just Validator
    if hasattr(validator, "id") and validator.id is not None:  # type: ignore
        ids[validator.id] = validator  # type: ignore

    for sub_validator in validator.get_subschema_validators():
        ids.update(generate_context(validator=sub_validator))

    return ids


def add_context_to_ref_validators(validator: typing.Union["AValidator"], context: Context):
    if isinstance(validator, Ref):
        validator.set_context(context)

    for sub_validators in validator.get_subschema_validators():
        add_context_to_ref_validators(validator=sub_validators, context=context)


class Ref(AValidator):

    def __init__(self, value):
        self.value = value
        self.context: Context = None

    def validate(self, instance):
        if self.context is None:
            return ValidationResult(ok=True)
        if self.value in self.context:
            return self.context[self.value].validate(instance)
        else:
            # this is temporary, probably need to do something else
            raise Exception("unable to fix this reference")
        return ValidationResult(ok=True)

    def set_context(self, context):
        self.context = context

    def __eq__(self, other) -> bool:
        if not isinstance(other, Ref):
            return NotImplemented
        return self.value == other.value
