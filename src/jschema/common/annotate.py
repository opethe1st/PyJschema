import typing as t

from .instance import Dict, Instance, List
from .utils import append


def annotate(obj, location="#") -> t.Union[Instance, Dict, List]:
    if isinstance(obj, list):
        return List(
            [
                annotate(obj=value, location=append(location, i))
                for i, value in enumerate(obj)
            ],
            location=location,
        )
    elif isinstance(obj, dict):
        return Dict(
            {
                key: annotate(obj=value, location=append(location, key))
                for key, value in obj.items()
            },
            location=location,
        )
    else:
        return Instance(value=obj, location=location)


# TODO(ope): use deannotate wherever it is useful, + Add tests
def deannotate(instance: Instance):
    if isinstance(instance, List):
        return [deannotate(instance=value) for value in instance]
    elif isinstance(instance, Dict):
        return {
            key: deannotate(instance=value) for key, value in instance.items()
        }
    else:
        return instance.value
