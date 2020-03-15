import contextlib
import contextvars
import functools
import json
import os
from dataclasses import dataclass, field
from typing import List

from uritools import urijoin, urisplit

OUTPUT: contextvars.ContextVar = contextvars.ContextVar("output")


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
            with open(
                os.path.join(
                    BASE,
                    self.authority_to_local_location[res.authority],
                    res.path.lstrip("/"),
                )+".json"
            ) as file:
                return json.load(file)
        else:
            raise Exception(f"Unable to locate this authority: {self.authority}")


def validate_only(type_):
    "this is makes sure that we only validate instance of the correct type"

    def wrapper(validate):
        @functools.wraps(validate)
        def wrapped_function(self, instance, location):
            if isinstance(instance, type_):
                return validate(self=self, instance=instance, location=location)
            else:
                return True

        return wrapped_function

    return wrapper


@dataclass
class ValidationResult:
    message: str
    keywordLocation: str
    location: str
    sub_results: List["ValidationResult"] = field(default_factory=list)

    def __bool__(self):
        return False
