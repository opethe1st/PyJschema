import abc
import numbers
import typing as t
from collections.abc import Mapping, Sequence

from jschema.common import ValidationResult

JsonType = t.Union[str, numbers.Number, bool, None, Mapping, Sequence]


class AValidator(abc.ABC):
    id = None
    base_uri = None  # if $id was set in the schema this Validator was created from
    anchor = None
    location: t.Optional[str] = None

    def __init__(self, **kwargs):
        pass

    @abc.abstractmethod
    def validate(self, instance: JsonType) -> ValidationResult:
        raise NotImplementedError

    def subschema_validators(self) -> t.Iterable["AValidator"]:
        yield from []


class KeywordGroup(AValidator):
    """
    Validator for a group of keywords that are dependent on each other.
    This also included the case where there is one validator
    """

    pass


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
                        **{keyword: schema.get(keyword) for keyword in keywords}
                    )
                )

    def validate(self, instance):
        results = []
        messages = []
        if self.type_ is not None and not isinstance(instance, self.type_):
            messages.append(f"instance is not a {self.type_}")
        if messages:
            raise Exception()
            return ValidationResult(ok=False, messages=messages)

        results = list(
            filter(
                (lambda res: not res.ok),
                (validator.validate(instance) for validator in self._validators),
            )
        )

        if not results and not messages:
            return ValidationResult(ok=True)
        else:
            raise Exception()
            return ValidationResult(ok=False, messages=messages, children=results)

    def subschema_validators(self):
        yield from self._validators
