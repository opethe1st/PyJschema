import typing as t

from jschema.common import AValidator, ValidationResult

from .constants import KEYWORDS_TO_VALIDATOR, TYPE_TO_TYPE_VALIDATORS
from .types_validator import Types
from jschema.draft_2019_09.referencing import Ref
from .defs import Defs


class Validator(AValidator):
    def __init__(self, schema):
        self.location = schema.location
        self._validators: t.List[AValidator] = []

        if "$defs" in schema.value:
            self._validators.append(Defs(schema=schema))
        if "$ref" in schema.value:
            self._validators.append(Ref(schema=schema))
            # return earlier because all other keywords are ignored when there is a $ref
            # - kinda think this is actually different in draft_2019_09
            return

        for key, ValidatorClass in KEYWORDS_TO_VALIDATOR.items():
            if key in schema.value:
                self._validators.append(ValidatorClass(schema=schema))

        if "$anchor" in schema.value:
            self.anchor = "#" + schema.value["$anchor"].value

        if "$id" in schema.value:
            self.id = schema.value["$id"].value.rstrip('#')

        if "type" in schema.value:
            if isinstance(schema.value["type"].value, list):
                self._validators.append(Types(schema=schema))
            else:
                if schema.value["type"].value in TYPE_TO_TYPE_VALIDATORS:
                    self._validators.append(
                        TYPE_TO_TYPE_VALIDATORS[schema.value["type"].value](schema=schema)
                    )
        else:
            # could be any of the types
            self._validators.append(Types(schema=schema))

    # hm.. this is the same as the method in Type.
    def validate(self, instance):
        results = []
        for validator in self._validators:
            result = validator.validate(instance)

            if not result.ok:
                results.append(result)

        if not results:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(
                ok=False,
                messages=["error while validating this instance"],
                children=results,
            )

    # hm.. this is the same as the method in Type.
    def subschema_validators(self):
        for validator in self._validators:
            yield validator
