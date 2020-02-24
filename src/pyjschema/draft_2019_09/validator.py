import itertools
import typing as t

from pyjschema.common import AValidator, ValidationError
from pyjschema.exceptions import SchemaError

from .constants import KEYWORD_TO_VALIDATOR
from .types.common import validate_instance_against_all_validators


KEYWORDS_THAT_REQUIRE_ANNOTATION_COLLECTION = set(
    ["unevaluatedProperties", "unevaluatedItems"]
)


class Validator(AValidator):
    """
    This corresponds to a schema
    """

    def __init__(self, schema, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        unsupported_keywords = KEYWORDS_THAT_REQUIRE_ANNOTATION_COLLECTION & set(
            schema.keys()
        )
        if unsupported_keywords:
            raise SchemaError(
                "Unable to process this Schema because this library doesn't support annotation collection"
                f" - which is required for these keywords - {unsupported_keywords} present in the schema"
            )
        self._validators: t.List[AValidator] = set()

        self.recursiveAnchor = schema.get("$recursiveAnchor", False)

        if "$anchor" in schema:
            self.anchor = "#" + schema["$anchor"]

        for key, ValidatorClass in KEYWORD_TO_VALIDATOR.items():
            if key in schema:
                self._validators.add(
                    ValidatorClass(schema=schema, location=location, parent=self)
                )

    def __call__(self, instance):
        errors = validate_instance_against_all_validators(
            validators=self._validators, instance=instance
        )
        first_result = next(errors, True)
        if first_result:
            return True
        else:
            return ValidationError(
                messages=["error while validating this instance"],
                children=itertools.chain([first_result], errors),
            )

    def sub_validators(self):
        yield from self._validators

    def __repr__(self):
        return f"Validator(validators={self._validators})"
