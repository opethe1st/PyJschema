import typing as t

from jschema.common import AValidator, Dict, ValidationError

from .constants import TYPE_TO_TYPE_VALIDATORS


class Types(AValidator):
    def __init__(self, schema: Dict):
        self._validators: t.List[AValidator] = []
        if "type" in schema:
            types: t.Iterable[str] = [item.value for item in schema["type"]]
        else:
            # if there is no type, then try all the types
            # TODO(ope): optimize this later
            types = TYPE_TO_TYPE_VALIDATORS.keys()

        for type_ in types:
            if type_ in TYPE_TO_TYPE_VALIDATORS:
                self._validators.append(TYPE_TO_TYPE_VALIDATORS[type_](schema=schema))

    def validate(self, instance):
        results = []

        for validator in self._validators:
            result = validator.validate(instance)

            if result:
                return result
            else:
                results.append(result)

        return ValidationError(
            messages=["error while validating this instance"],
            children=results,
        )

    # Forgot this too - enforce with abc abstract?
    def subschema_validators(self):
        yield from self._validators
