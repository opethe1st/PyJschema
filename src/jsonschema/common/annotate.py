from .instance import Instance
from .utils import append


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


# TODO(ope): use deannotate wherever it is useful, + Add tests
def deannotate(instance: Instance):
    if isinstance(instance.value, list):
        return [
            deannotate(instance=value)
            for value in instance.value
        ]
    elif isinstance(instance.value, dict):
        return {
                key: deannotate(instance=value)
                for key, value in instance.value.items()
            }
    else:
        return instance.value
