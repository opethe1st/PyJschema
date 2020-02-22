from pyjschema.common import Keyword


class Defs(Keyword):

    keyword = "$defs"

    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        from .validator_construction import build_validator

        self._validators = {
            key: build_validator(
                schema=value, location=f"{location}/{key}", parent=self
            )
            for key, value in self.value.items()
        }

    def validate(self, instance):
        return True

    def sub_validators(self):
        yield from self._validators.values()

    def __repr__(self):
        return f"Defs(keys={list(self._validators.keys())})"
