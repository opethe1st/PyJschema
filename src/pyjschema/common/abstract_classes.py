import abc
import numbers
import typing
from collections.abc import Mapping, Sequence

from pyjschema.exceptions import InternalError

from .validation_error import ValidationError

JsonType = typing.Union[str, numbers.Number, bool, None, Mapping, Sequence]


class AValidator(abc.ABC):
    id = None  # and remove this line
    base_uri = None
    anchor = None

    def __init__(self, schema: typing.Dict, location=None, parent=None):
        schema = {} if isinstance(schema, bool) else schema
        self.parent = parent
        self.id = self.base_uri = schema["$id"] if schema.get("$id") else None
        self.location = location
        self.anchor = schema["$anchor"] if schema.get("$anchor") else None

    @abc.abstractmethod
    def __call__(self, instance: JsonType) -> ValidationError:
        raise NotImplementedError

    def sub_validators(self) -> typing.Iterable["AValidator"]:
        yield from []


class KeywordGroup(AValidator):
    """
    Validator for a group of keywords that are dependent on each other.
    """

    def __init__(self):
        raise NotImplementedError

    def sub_validators(self) -> typing.Iterable["AValidator"]:
        raise NotImplementedError


class Keyword(AValidator):
    keyword: typing.Optional[str] = None

    def __init__(self, schema: dict, location=None, parent=None):
        if self.keyword is None:
            raise InternalError("You need to provide a keyword to this function")
        self.value = schema[self.keyword]
        super().__init__(schema=schema, location=location, parent=parent)
        self.location = f"{self.location}/{self.keyword}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"
