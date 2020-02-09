from pyjschema.common import Dict, KeywordGroup


class Defs(KeywordGroup):
    """
    This is corresponds to the $defs keyword
    """

    def __init__(self, schema: Dict, location=None):
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
