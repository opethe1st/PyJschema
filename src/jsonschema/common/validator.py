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
    pass
