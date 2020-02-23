class SchemaError(Exception):
    pass


class InstanceError(Exception):
    pass


class ProgrammerError(Exception):
    """These are errors that should never been shown to users but to aid when writing code"""

    pass
