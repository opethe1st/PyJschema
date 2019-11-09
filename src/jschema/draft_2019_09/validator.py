import typing as t

from jschema.common import AValidator, ValidationResult


class Validator(AValidator):
    def __init__(self):
        self._validators: t.List[AValidator] = []

    def add_validator(self, validator: AValidator):
        self._validators.append(validator)

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
