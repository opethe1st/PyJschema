import contextlib
import contextvars

from uritools import urisplit, uriunsplit


def to_canonical_uri(current_base_uri, uri):
    split = urisplit(uri)
    if split.scheme is None and split.authority is None:
        current_base_uri_split = urisplit(current_base_uri)
        path = split.path if split.path and split.path[0] == "/" else "/" + split.path
        path = current_base_uri_split.path if path in ["/", ""] else path
        return uriunsplit(
            [
                current_base_uri_split.scheme,
                current_base_uri_split.authority,
                path,
                split.query,
                split.fragment,
            ]
        )
    return uri


@contextlib.contextmanager
def context(contextvar: contextvars.ContextVar, value):
    token = contextvar.set(value)
    yield
    contextvar.reset(token)
