import itertools
import typing as t

from jschema.common import AValidator, KeywordGroup, ValidationError

from .common import validate_instance_against_all_validators


class Type(AValidator):
    """Validator for a type"""

    KEYWORDS_TO_VALIDATOR: t.Dict[
        t.Tuple[str, ...], t.Union[t.Type[KeywordGroup], t.Type[KeywordGroup]]
    ] = {}
    type_: t.Optional[t.Type] = None

    def __init__(self, schema):
        self._validators: t.List[AValidator] = []
        for keywords in self.KEYWORDS_TO_VALIDATOR:

            if any(schema.get(keyword) is not None for keyword in keywords):
                self._validators.append(
                    self.KEYWORDS_TO_VALIDATOR[keywords](
                        schema=schema
                    )
                )

    def validate(self, instance):
        messages = []
        if self.type_ is not None and not isinstance(instance, self.type_):
            messages.append(f"instance is not a {self.type_}")
        if messages:
            return ValidationError(messages=messages)

        errors = validate_instance_against_all_validators(
            validators=self._validators, instance=instance
        )
        # default to True if exhausted since that means that there were no errors
        first_result = next(errors, True)

        if first_result and not messages:
            return True
        else:
            return ValidationError(
                messages=messages, children=itertools.chain([first_result], errors)
            )

    def subschema_validators(self):
        yield from self._validators
