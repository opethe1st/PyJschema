from typing import Dict

from uritools import urijoin

from pyjschema.common import AValidator, Keyword, KeywordGroup

from .ref import RecursiveRef, Ref
from .validator import Validator


def _populate_uri_to_validator(
    validator: AValidator,
    root_base_uri,
    uri_to_validator: Dict,
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

    if validator.anchor:
        uri_to_validator[
            (urijoin(validator.base_uri or "", validator.anchor))
        ] = validator

    for sub_validator in validator.sub_validators():
        _populate_uri_to_validator(
            validator=sub_validator,
            root_base_uri=root_base_uri,
            uri_to_validator=uri_to_validator,
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
    uri_to_validator = {"": root_validator, "#": root_validator}
    _populate_uri_to_validator(
        validator=root_validator,
        root_base_uri=root_validator.base_uri or "",
        uri_to_validator=uri_to_validator,
    )
    _resolve_references(
        validator=root_validator, uri_to_validator=uri_to_validator,
    )
    return uri_to_validator
