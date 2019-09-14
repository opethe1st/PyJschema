import abc
import collections.abc as ca
import numbers
import typing

from jsonschema.common import ValidationResult

JsonType = typing.Union[str, numbers.Number, bool, None, ca.Mapping, ca.Sequence]


# TODO(ope), probably rename this to AValidator since it is not purely an interface
class IValidator(abc.ABC):

    def __init__(self, **kwargs):
        pass

    @abc.abstractmethod
    def validate(self, instance: JsonType) -> ValidationResult:
        pass
