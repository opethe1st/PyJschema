import typing as t

from jschema.common import AValidator

from .ref import Context, Ref


def generate_context(validator: AValidator) -> Context:
    uri_to_validator: Context = {}

    if validator.anchor is not None:
        uri_to_validator[validator.id + validator.anchor] = validator
    if validator.location is not None:
        uri_to_validator[validator.location] = validator

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
        attach_base_URIs(validator=sub_validator, parent_URI=validator.id)


def add_context_to_ref_validators(validator: t.Union[AValidator], context: Context):
    if isinstance(validator, Ref):
        validator.set_context(context)

    for sub_validators in validator.subschema_validators():
        add_context_to_ref_validators(validator=sub_validators, context=context)
