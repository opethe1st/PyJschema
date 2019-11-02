import typing as t

import dataclasses
from .utils import append


@dataclasses.dataclass
class Instance:
    value: t.Any
    location: str


def annotate(obj, location="#") -> Instance:
    if isinstance(obj, list):
        return Instance(
            value=[
                annotate(obj=value, location=append(location, i))
                for i, value in enumerate(obj)
            ],
            location=location,
        )
    elif isinstance(obj, dict):
        return Instance(
            value={
                key: annotate(obj=value, location=append(location, key))
                for key, value in obj.items()
            },
            location=location,
        )
    else:
        return Instance(value=obj, location=location)
