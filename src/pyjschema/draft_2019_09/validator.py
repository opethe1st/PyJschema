import typing

from pyjschema.common import AValidator
from pyjschema.draft_2019_09.context import USE_SHORTCIRCUITING, VOCABULARIES
from pyjschema.exceptions import SchemaError

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
        self._validators: typing.Dict[str, AValidator] = dict()

        self.recursiveAnchor = schema.get("$recursiveAnchor", False)

        if "$anchor" in schema:
            self.anchor = "#" + schema["$anchor"]

        KEYWORD_TO_VALIDATOR = VOCABULARIES.get()

        for key, KeywordClass in KEYWORD_TO_VALIDATOR.items():
            if key in schema:
                self._validators[key] = KeywordClass(
                    schema=schema, location=location, parent=self
                )

    def __call__(self, instance, location=""):
        errors = validate_instance_against_all_validators(
            validators=self._validators, instance=instance, location=location
        )
        first_result = next(errors, True)
        if first_result:
            return True
        else:
            return False

    def sub_validators(self):
        yield from self._validators.values()

    def __repr__(self):
        return f"Validator(validators={self._validators})"


def validate_instance_against_all_validators(
    validators: typing.Dict[str, AValidator], instance, location
):
    if USE_SHORTCIRCUITING.get():
        results = (
            validator(instance=instance, location=location)
            for key, validator in validators.items()
        )
    else:
        results = [
            validator(instance=instance, location=location)
            for key, validator in validators.items()
        ]
    yield from filter(
        lambda res: not res,
        results,
    )
