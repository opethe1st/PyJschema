import abc
import numbers
import typing as t
from collections.abc import Mapping, Sequence

from jschema.common import ValidationError

JsonType = t.Union[str, numbers.Number, bool, None, Mapping, Sequence]
# TODO: rename this file to abstract validator or something


class AValidator(abc.ABC):
    id = None
    base_uri = None  # if $id was set in the schema this Validator was created from
    anchor = None
    location: t.Optional[str] = None

    def __init__(self, **kwargs):
        pass

    @abc.abstractmethod
    def validate(self, instance: JsonType) -> ValidationError:
        raise NotImplementedError

    def subschema_validators(self) -> t.Iterable["AValidator"]:
        yield from []


class KeywordGroup(AValidator):
    """
    Validator for a group of keywords that are dependent on each other.
    This also included the case where there is one validator
    """

    pass
