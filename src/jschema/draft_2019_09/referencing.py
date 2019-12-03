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
        validator.base_uri = uri  # this should probably be in the constructor
        validator.id = uri

    for sub_validator in validator.subschema_validators():
        attach_base_URIs(validator=sub_validator, parent_URI=validator.id)


def generate_context(validator: AValidator, root_base_uri) -> t.Tuple[Context, t.Dict]:
    """
    This needs to be run after attach_base_URIs because attach_base_URIs propagates
    propagated to the children schemas.
    This returns a dictionary with all the relative locations from the root schema +
    resolved anchors
    To get the
    """
    uri_to_validator: Context = {}
    base_uri_to_location: t.Dict = {}

    if validator.base_uri:
        uri_to_validator[validator.base_uri] = validator
        base_uri_to_location[validator.base_uri] = validator.location

    # This supports just canonical URIs
    if validator.id is not None:
        if validator.anchor is not None:
            uri_to_validator[validator.id + validator.anchor] = validator

        # save the relative location
        if validator.location is not None:
            uri_to_validator[validator.location] = validator

    for sub_validator in validator.subschema_validators():
        sub_uri_to_validator, sub_base_uri_to_location = generate_context(
            validator=sub_validator, root_base_uri=root_base_uri
        )
        uri_to_validator.update(sub_uri_to_validator)
        base_uri_to_location.update(sub_base_uri_to_location)

    return uri_to_validator, base_uri_to_location


def add_context_to_ref_validators(
    validator: t.Union[AValidator], context: Context, base_uri_to_abs_location
):
    if isinstance(validator, Ref):
        validator.set_context(context)
        validator.set_base_uri_to_abs_location(base_uri_to_abs_location)

    for sub_validators in validator.subschema_validators():
        add_context_to_ref_validators(
            validator=sub_validators,
            context=context,
            base_uri_to_abs_location=base_uri_to_abs_location,
        )
