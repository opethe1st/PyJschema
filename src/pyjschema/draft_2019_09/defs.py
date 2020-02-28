from pyjschema.common import Keyword
from pyjschema.draft_2019_09.context import BUILD_VALIDATOR


class Defs(Keyword):

    keyword = "$defs"

    def __init__(self, schema: dict, location=None, parent=None):
        super().__init__(schema=schema, location=location, parent=parent)
        build_validator = BUILD_VALIDATOR.get()

        self._validators = {
            key: build_validator(
                schema=value, location=f"{self.location}/{key}", parent=self
            )
            for key, value in self.value.items()
        }

    def __call__(self, instance, output, location=None):
        return True

    def sub_validators(self):
        yield from self._validators.values()

    def __repr__(self):
        return f"Defs(keys={list(self._validators.keys())})"
