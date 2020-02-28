import contextlib
import contextvars
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
