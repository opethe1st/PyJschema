import abc
import numbers
import typing
from collections.abc import Mapping, Sequence

from pyjschema.utils import to_canonical_uri
from pyjschema.exceptions import ProgrammerError

from .validation_error import ValidationError

JsonType = typing.Union[str, numbers.Number, bool, None, Mapping, Sequence]


class AValidator(abc.ABC):
    id = None  # and remove this line
    base_uri = None
    anchor = None

    def __init__(self, schema: typing.Dict, location=None, parent=None):
        schema = {} if isinstance(schema, bool) else schema
        self.schema = schema
        if "$id" in schema:
            self.id = to_canonical_uri(
                current_base_uri=parent.base_uri if parent else "", uri=schema["$id"]
            )
            self.base_uri = self.id
        else:
            self.base_uri = parent.base_uri if parent else ""
        self.parent = parent
        self.location = location
        self.anchor = schema.get("$anchor")

    @abc.abstractmethod
    def __call__(self, instance: JsonType) -> ValidationError:
        raise NotImplementedError

    def sub_validators(self) -> typing.Iterable["AValidator"]:
        yield from []


class KeywordGroup(AValidator):
    """
    Validator for a group of keywords that are dependent on each other.
    """

    # I could do something similar to what I did for Keyword here by having a keyword class variable

    def sub_validators(self) -> typing.Iterable["AValidator"]:
        raise NotImplementedError

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.location == other.location

    def __hash__(self):
        return hash((self.location, self.parent, self.__class__.__name__))


class Keyword(AValidator):
    keyword: typing.Optional[str] = None

    def __init__(self, schema: dict, location, parent):
        if self.keyword is None:
            raise ProgrammerError("You need to provide a keyword to this function")
        self.value = schema[self.keyword]
        super().__init__(schema=schema, location=location, parent=parent)
        self.location = f"{self.location}/{self.keyword}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.value == other.value

    def __hash__(self):
        return hash(str((self.value, self.__class__)))
