import abc
import numbers
import typing as t
from collections.abc import Mapping, Sequence

from jsonschema.common import ValidationResult

JsonType = t.Union[str, numbers.Number, bool, None, Mapping, Sequence]


Schema = t.Dict


class AValidator(abc.ABC):
    id = None
    anchor = None

    def __init__(self, **kwargs):
        pass

    @abc.abstractmethod
    def validate(self, instance: JsonType) -> ValidationResult:
        pass

    def subschema_validators(self) -> t.Iterable["AValidator"]:
        return []


class KeywordGroup(AValidator):
    """Validator for a group of keyword that are dependent on each other"""

    pass


class Keyword(AValidator):
    """Validator for a keyword"""

    pass


class Type(AValidator):
    """Validator for a type"""

    KEYWORDS_TO_VALIDATOR: t.Dict[
        t.Tuple[str, ...], t.Union[t.Type[Keyword], t.Type[KeywordGroup]]
    ] = {}
    type_: t.Optional[t.Type] = None

    def __init__(self, schema):
        self._validators: t.List[AValidator] = []
        for keywords in self.KEYWORDS_TO_VALIDATOR:

            if any(schema.value.get(keyword) is not None for keyword in keywords):
                self._validators.append(
                    self.KEYWORDS_TO_VALIDATOR[keywords](
                        **{keyword: schema.value.get(keyword) for keyword in keywords}
                    )
                )

    def validate(self, instance):
        results = []
        messages = []
        if self.type_ is not None and not isinstance(instance, self.type_):
            messages.append(f"instance is not a {self.type_}")

        results = list(
            filter(
                (lambda res: not res.ok),
                (validator.validate(instance) for validator in self._validators),
            )
        )

        if not results and not messages:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(ok=False, messages=messages, children=results)

    def subschema_validators(self):
        # maybe optimize by not returning validators that don't have schemas embedded
        for validator in self._validators:
            yield validator
