import abc
import numbers
import typing
from collections.abc import Mapping, Sequence

from jsonschema.common import ValidationResult

JsonType = typing.Union[str, numbers.Number, bool, None, Mapping, Sequence]


class AValidator(abc.ABC):

    def __init__(self, **kwargs):
        pass

    @abc.abstractmethod
    def validate(self, instance: JsonType) -> ValidationResult:
        pass

    def subschema_validators(self) -> typing.Iterable["AValidator"]:
        return []


class KeywordGroup(AValidator):
    '''Validator for a group of keyword that are dependent on each other'''
    pass


class Keyword(AValidator):
    '''Validator for a keyword'''
    pass


class Type(AValidator):
    '''Validator for a type'''
    KEYWORDS_TO_VALIDATOR: typing.Dict[typing.Tuple[str, ...], typing.Type[AValidator]] = {}
    type_: typing.Optional[typing.Type] = None  # this is required too

    def __init__(self, schema):
        self._validators = []
        for keywords in self.KEYWORDS_TO_VALIDATOR:

            if any(schema.get(keyword) is not None for keyword in keywords):
                self._validators.append(
                    self.KEYWORDS_TO_VALIDATOR[keywords](**{keyword: schema.get(keyword) for keyword in keywords})
                )

    def validate(self, instance):
        results = []
        messages = []
        if not isinstance(instance, self.type_):
            messages.append(f'instance is not a {self.type_}')
        for validator in self._validators:
            result = validator.validate(instance)
            if not result.ok:
                results.append(result)

        if not results and not messages:
            return ValidationResult(ok=True)
        else:
            return ValidationResult(
                ok=False,
                messages=messages,
                children=results
            )

    def subschema_validators(self):
        # maybe optimize by not returning validators that don't have schemas embedded
        for validator in self._validators:
            yield validator
