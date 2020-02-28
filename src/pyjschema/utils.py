import contextlib
import contextvars

from uritools import urijoin


def to_canonical_uri(current_base_uri, uri):
    return urijoin(current_base_uri, uri)


@contextlib.contextmanager
def context(contextvar: contextvars.ContextVar, value):
    token = contextvar.set(value)
    yield
    contextvar.reset(token)
