import contextvars


VOCABULARIES: contextvars.ContextVar = contextvars.ContextVar("vocabularies")
BUILD_VALIDATOR: contextvars.ContextVar = contextvars.ContextVar("build_validator")
USE_SHORTCIRCUITING: contextvars.ContextVar = contextvars.ContextVar("USE_SHORTCIRCUITING")
