from typing import Dict, Tuple

from uritools import urijoin

from pyjschema.common import AValidator

from .ref import Ref


def _attach_base_URIs(validator: AValidator, parent_URI):
    if not validator.base_uri:
        validator.base_uri = parent_URI

    for sub_validator in validator.sub_validators():
        _attach_base_URIs(validator=sub_validator, parent_URI=validator.base_uri)


def _generate_context(
    validator: AValidator, root_base_uri, uri_to_validator, uri_to_root_location
):
    """
    This needs to be run after _attach_base_URIs because _attach_base_URIs propagates
    the base_URIs through the subschemas.
    returns a dictionary with uri to validator.
    the uris are of three types.
    - canonical id
    - canonical id + location
    - canonical id + anchor
    """

    uri_to_validator[urijoin(root_base_uri, "#" + validator.location)] = validator

    if validator.id:
        validator_id = validator.id.rstrip("/")
        uri_to_validator[validator_id] = validator
        uri_to_root_location[validator_id] = validator.location

    if validator.anchor and validator.base_uri:
        # print("base_uri, anchor", validator.base_uri, validator.anchor)
        uri_to_validator[urijoin(validator.base_uri + "#", validator.anchor)] = validator

    for sub_validator in validator.sub_validators():
        _generate_context(
            validator=sub_validator,
            root_base_uri=root_base_uri,
            uri_to_validator=uri_to_validator,
            uri_to_root_location=uri_to_root_location,
        )


def _resolve_references(validator: AValidator, uri_to_validator, uri_to_root_location):
    if isinstance(validator, Ref):
        validator.resolve(
            uri_to_validator=uri_to_validator, uri_to_root_location=uri_to_root_location
        )

    for sub_validator in validator.sub_validators():
        _resolve_references(
            validator=sub_validator,
            uri_to_validator=uri_to_validator,
            uri_to_root_location=uri_to_root_location,
        )


def resolve_references(root_validator):
    _attach_base_URIs(validator=root_validator, parent_URI=None)
    uri_to_root_location = {"": root_validator.base_uri, "#": root_validator.base_uri}
    uri_to_validator = {"": root_validator, "#": root_validator}
    _generate_context(
        validator=root_validator,
        root_base_uri=root_validator.base_uri or "",
        uri_to_root_location=uri_to_root_location,
        uri_to_validator=uri_to_validator,
    )
    _resolve_references(
        validator=root_validator,
        uri_to_validator=uri_to_validator,
        uri_to_root_location=uri_to_root_location,
    )
