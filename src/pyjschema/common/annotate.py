import typing as t

from .primitive_types_wrappers import Dict, Primitive, List


def annotate(obj, location="") -> t.Union[Primitive, Dict, List]:
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
        return Primitive(value=obj, location=location)


def deannotate(instance: Primitive):
    if isinstance(instance, List):
        return [deannotate(instance=value) for value in instance]
    elif isinstance(instance, Dict):
        return {key: deannotate(instance=value) for key, value in instance.items()}
    else:
        return instance.value


# TODO(ope): support escaping
def append(location, value):
    return "{location}/{value}".format(location=location, value=value)
