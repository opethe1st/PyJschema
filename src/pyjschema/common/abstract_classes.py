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
        self.parent = parent
        self.id = self.base_uri = schema.get("$id")
        self.location = location
        self.anchor = schema.get("$anchor")
        self._set_base_uri()

    # to replace _set_to_canonical_uri once I can use the same init in KeywordGroup
    def _set_base_uri(self):
        if not self.base_uri:
            self.base_uri = self.parent.base_uri if self.parent else ""
        elif self.id is not None:
            self.id = self.base_uri = to_canonical_uri(
                current_base_uri=self.parent.base_uri if self.parent else "", uri=self.base_uri
            )

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


class Keyword(AValidator):
    keyword: typing.Optional[str] = None

    def __init__(self, schema: dict, location=None, parent=None):
        if self.keyword is None:
            raise ProgrammerError("You need to provide a keyword to this function")
        self.value = schema[self.keyword]
        super().__init__(schema=schema, location=location, parent=parent)
        self.location = f"{self.location}/{self.keyword}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"
