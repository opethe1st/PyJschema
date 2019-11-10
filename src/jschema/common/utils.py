import re


# TODO(ope): support escaping
def append(location, value):
    return "{location}/{value}".format(location=location, value=value)


# TODO(ope): move to util or something + better name
def re_compile(pattern):
    if pattern.startswith("^"):
        value = pattern
    else:
        value = ".*" + pattern
    return re.compile(value)
