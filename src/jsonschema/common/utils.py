# TODO(ope): support escaping
def append(location, value):
    return "{location}/{value}".format(location=location, value=value)