import abc
import numbers
import typing
from collections.abc import Mapping, Sequence

from .validation_error import ValidationError

JsonType = typing.Union[str, numbers.Number, bool, None, Mapping, Sequence]


class AValidator(abc.ABC):
    id = None  # and remove this line
    base_uri = None
    anchor = None

    def __init__(self, schema: typing.Dict, location=None):
        schema = {} if isinstance(schema, bool) else schema
        self.id = self.base_uri = (
            schema["$id"] if schema.get("$id") else None
        )
        self.location = location
        self.anchor = schema["$anchor"] if schema.get("$anchor") else None

    @abc.abstractmethod
    def validate(self, instance: JsonType) -> ValidationError:
        raise NotImplementedError

    def sub_validators(self) -> typing.Iterable["AValidator"]:
        yield from []


class KeywordGroup(AValidator):
    """
    Validator for a group of keywords that are dependent on each other.
    This also includes the case where there is one keyword
    """

    pass
