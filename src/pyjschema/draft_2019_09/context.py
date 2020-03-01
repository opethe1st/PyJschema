import contextvars


VOCABULARIES: contextvars.ContextVar = contextvars.ContextVar("vocabularies")
BUILD_VALIDATOR: contextvars.ContextVar = contextvars.ContextVar("build_validator")

