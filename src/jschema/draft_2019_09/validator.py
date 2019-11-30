import itertools
import typing as t

from jschema.common import AValidator, List, ValidationError
from jschema.draft_2019_09.referencing import Ref

from .constants import KEYWORDS_TO_VALIDATOR, TYPE_TO_TYPE_VALIDATORS
from .defs import Defs
from .types.common import validate_instance_against_all_validators
from .types_validator import Types


class Validator(AValidator):
    """
    This corresponds to a schema
    """

    def __init__(self, schema):
        self.location = schema.location
        self._validators: t.List[AValidator] = []

        if "$defs" in schema:
            self._validators.append(Defs(schema=schema))
        if "$ref" in schema:
            self._validators.append(Ref(schema=schema))
            # return earlier because all other keywords are ignored when there is a $ref
            # - kinda think this is actually different in draft_2019_09
            return

        for key, ValidatorClass in KEYWORDS_TO_VALIDATOR.items():
            if key in schema:
                self._validators.append(ValidatorClass(schema=schema))

        if "$anchor" in schema:
            self.anchor = "#" + schema["$anchor"].value

        if "$id" in schema:
            self.id = schema["$id"].value.rstrip("#")

        if "type" in schema:
            if isinstance(schema["type"], List):
                self._validators.append(Types(schema=schema))
            else:
                if schema["type"].value in TYPE_TO_TYPE_VALIDATORS:
                    self._validators.append(
                        TYPE_TO_TYPE_VALIDATORS[schema["type"].value](schema=schema)
                    )
        else:
            # could be any of the types
            self._validators.append(Types(schema=schema))

    # hm.. this is the same as the method in Type.
    def validate(self, instance):
        # can move this to a function that take in a list of validators and an instance
        # then yield the errors as they occur
        error_generator = validate_instance_against_all_validators(validators=self._validators, instance=instance)
        first_error = next(error_generator, True)
        if first_error:
            return True
        else:
            return ValidationError(
                messages=["error while validating this instance"],
                children=itertools.chain([first_error], error_generator),
            )

    # TODO(ope): hm.. this is the same as the method in Type.
    def subschema_validators(self):
        yield from self._validators
