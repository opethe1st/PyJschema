import contextlib
import contextvars
from urllib import parse


def to_canonical_uri(current_base_uri, uri):
    return parse.urljoin(current_base_uri, uri)


@contextlib.contextmanager
def context(contextvar: contextvars.ContextVar, value):
    token = contextvar.set(value)
    yield
    contextvar.reset(token)
