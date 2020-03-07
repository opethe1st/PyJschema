from typing import Optional


class SchemaError(Exception):
    def __init__(self, message, details: Optional[dict] = None):
        super().__init__()
        details = details if details else {}
        self.message = message
        self.details = details


class ValidationError(Exception):
    def __init__(self, message, details: Optional[dict] = None):
        super().__init__()
        details = details if details else {}
        self.message = message
        self.details = details


class ProgrammerError(Exception):
    """These are errors that should never been shown to users but to aid when writing code"""

    pass
