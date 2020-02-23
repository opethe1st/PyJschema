from typing import Dict

from uritools import urijoin

from pyjschema.common import AValidator, KeywordGroup, Keyword

from .ref import Ref, RecursiveRef
from pyjschema.utils import to_canonical_uri
from .validator import Validator


# # actually, I could do this in the constructor instead of here.
# doesnt work but not sure why
def _set_to_canonical_uri(validator: AValidator, parent_URI):
    if not validator.base_uri:
        validator.base_uri = parent_URI
    elif validator.id is not None:
        validator.id = validator.base_uri = to_canonical_uri(
            current_base_uri=parent_URI, uri=validator.base_uri
        )

    for sub_validator in validator.sub_validators():
        _set_to_canonical_uri(validator=sub_validator, parent_URI=validator.base_uri)


def _generate_context(
    validator: AValidator,
    root_base_uri,
    uri_to_validator: Dict,
    uri_to_root_location: Dict,
):
    """
    This needs to be run after _set_to_canonical_uri because _set_to_canonical_uri propagates
    the base_URIs through the subschemas.
    returns a dictionary of the uri to validator mapping
    the uris are of three types.
    - canonical id
    - canonical id + location
    - canonical id + anchor
    """
    if isinstance(validator, (Keyword, AValidator)) and not isinstance(validator, KeywordGroup) and validator.location:
        uri_to_validator[urijoin(root_base_uri, "#" + validator.location)] = validator

    if validator.id is not None and isinstance(validator, Validator):
        validator_id = validator.id.rstrip("/")
        uri_to_validator[validator_id] = validator
        uri_to_root_location[validator_id] = validator.location

    if validator.anchor:
        uri_to_validator[
            (urijoin(validator.base_uri or "", validator.anchor))
        ] = validator

    for sub_validator in validator.sub_validators():
        _generate_context(
            validator=sub_validator,
            root_base_uri=root_base_uri,
            uri_to_validator=uri_to_validator,
            uri_to_root_location=uri_to_root_location,
        )


def _resolve_references(validator: AValidator, uri_to_validator: Dict):

    if isinstance(validator, Ref):
        validator.resolve(uri_to_validator=uri_to_validator)

    if isinstance(validator, RecursiveRef):
        validator.resolve()

    for sub_validator in validator.sub_validators():
        _resolve_references(
            validator=sub_validator, uri_to_validator=uri_to_validator,
        )


def resolve_references(root_validator):
    _set_to_canonical_uri(
        validator=root_validator, parent_URI=root_validator.base_uri or ""
    )
    uri_to_root_location = {"": root_validator.base_uri, "#": root_validator.base_uri}
    uri_to_validator = {"": root_validator, "#": root_validator}
    _generate_context(
        validator=root_validator,
        root_base_uri=root_validator.base_uri or "",
        uri_to_root_location=uri_to_root_location,
        uri_to_validator=uri_to_validator,
    )
    _resolve_references(
        validator=root_validator, uri_to_validator=uri_to_validator,
    )
    return uri_to_validator
