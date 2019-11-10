import re
import typing as t

from jschema.common import AValidator

from .ref import Context, Ref


FRAGMENT_REGEX = re.compile(pattern=r".*#.*")
BASE_URI_REGEX = re.compile(pattern=r"http.*")


def get_base_URI_from_URI_part(parent_URI, base_URI):
    # if this is something like
    if BASE_URI_REGEX.match(base_URI):
        return base_URI
    elif FRAGMENT_REGEX.match(base_URI):
        raise Exception("return $id should not contain a fragment")
    else:
        parts = parent_URI.strip("/").split("/")
        parts[-1] = base_URI.strip("/")
        return "/".join(parts)


def attach_base_URIs(validator: AValidator, parent_URI):
    if validator.id is None:
        validator.id = parent_URI
    else:
        uri = get_base_URI_from_URI_part(parent_URI=parent_URI, base_URI=validator.id)
        validator.base_uri = uri
        validator.id = uri

    for sub_validator in validator.subschema_validators():
        attach_base_URIs(validator=sub_validator, parent_URI=validator.id)


def generate_context(validator: AValidator, root_base_uri) -> Context:
    """
    This needs to be run after attach_base_URIs so that the ids are
    propagated to the children schemas.
    This returns a dictionary with all the relative locations from the root schema +
    resolved anchors
    To get the
    """
    uri_to_validator: Context = {}

    if validator.base_uri:
        uri_to_validator[validator.base_uri] = validator

    # This supports just canonical URIs
    if validator.id is not None:
        # this is wrong because this validator.id is not unique across validators
        # do I need a new variable? to say if id was actually set or if its from a parent?
        #
        if validator.anchor is not None:
            uri_to_validator[validator.id + validator.anchor] = validator

        # save the relative location
        if validator.location is not None:
            uri_to_validator[root_base_uri + validator.location] = validator

    for sub_validator in validator.subschema_validators():
        sub_uri_to_validator = generate_context(
            validator=sub_validator, root_base_uri=root_base_uri
        )
        uri_to_validator.update(sub_uri_to_validator)

    return uri_to_validator


def add_context_to_ref_validators(validator: t.Union[AValidator], context: Context):
    if isinstance(validator, Ref):
        validator.set_context(context)

    for sub_validators in validator.subschema_validators():
        add_context_to_ref_validators(validator=sub_validators, context=context)


def resolve_uri(context, uri):

    return uri
