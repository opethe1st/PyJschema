from pyjschema.common import KeywordGroup


class Defs(KeywordGroup):
    """
    This is corresponds to the $defs keyword
    """

    def __init__(self, schema: dict, location=None):
        super().__init__(schema=schema, location=location)
        defs = schema["$defs"]
        from .validator_construction import build_validator

        self._validators = {
            key: build_validator(schema=value, location=f'{location}/{key}') for key, value in defs.items()
        }

    def validate(self, instance):
        return True

    def sub_validators(self):
        yield from self._validators.values()

    def __repr__(self):
        return f"Defs(keys={list(self._validators.keys())})"
