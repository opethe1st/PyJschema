import abc
import numbers
import typing as t
from collections.abc import Mapping, Sequence

from .validation_error import ValidationError
from .primitive_types_wrappers import Dict


JsonType = t.Union[str, numbers.Number, bool, None, Mapping, Sequence]


class AValidator(abc.ABC):
    id = None  # and remove this line
    base_uri = None
    anchor = None

    def __init__(self, schema: Dict):
        # TODO(Ope): call super in all the subclasses
        self.id = self.base_uri = schema.get("$id")
        self.location = schema.location
        self.anchor = schema.get("$anchor")

    @abc.abstractmethod
    def validate(self, instance: JsonType) -> ValidationError:
        raise NotImplementedError

    def sub_validators(self) -> t.Iterable["AValidator"]:
        yield from []


class KeywordGroup(AValidator):
    """
    Validator for a group of keywords that are dependent on each other.
    This also includes the case where there is one keyword
    """

    pass
