import contextlib
import contextvars
import functools
import json
import os

from uritools import urijoin, urisplit


def to_canonical_uri(current_base_uri, uri):
    return urijoin(current_base_uri, uri)


@contextlib.contextmanager
def context(contextvar: contextvars.ContextVar, value):
    token = contextvar.set(value)
    yield
    contextvar.reset(token)


class SchemaLoader:
    def __init__(self, authority_to_local_location):
        self.authority_to_local_location = authority_to_local_location

    def get(self, uri):
        BASE = os.path.dirname(__file__)
        res = urisplit(uri)
        if res.authority in self.authority_to_local_location:
            with open(os.path.join(BASE, self.authority_to_local_location[res.authority], res.path.lstrip('/'))) as file:
                return json.load(file)
        else:
            raise Exception(f"Unable to locate this authority: {self.authority}")


def validate_only(type_):
    "this is makes sure that we only validate instance of the correct type"

    def wrapper(validate):
        @functools.wraps(validate)
        def wrapped_function(self, instance, output, location):
            if isinstance(instance, type_):
                return validate(self=self, instance=instance, output=output, location=location)
            else:
                return True

        return wrapped_function

    return wrapper


def basic_output(error_message: str):
    "if this __call__ function evaluates to false, add this message to errors"
    def wrapper(validate):
        @functools.wraps(validate)
        def wrapped_function(self, instance, output, location):
            res = validate(self=self, instance=instance, output=output, location=location)
            if res is False:
                output["errors"].append(
                    {
                        "keywordLocation": self.location,
                        "instanceLocation": location,
                        "error": error_message
                    }
                )
            return res
        return wrapped_function
    return wrapper
