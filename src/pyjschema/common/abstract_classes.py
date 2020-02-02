import abc
import numbers
import typing as t
from collections.abc import Mapping, Sequence

from .annotate import deannotate
from .primitive_types_wrappers import Dict
from .validation_error import ValidationError

JsonType = t.Union[str, numbers.Number, bool, None, Mapping, Sequence]


class AValidator(abc.ABC):
    id = None  # and remove this line
    base_uri = None
    anchor = None

    def __init__(self, schema: Dict):
        self.id = self.base_uri = (
            deannotate(schema["$id"]) if schema.get("$id") else None
        )
        self.location = schema.location
        self.anchor = deannotate(schema["$anchor"]) if schema.get("$anchor") else None

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
