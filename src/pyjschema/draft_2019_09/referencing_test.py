import unittest

import parameterized  # type: ignore

from pyjschema.common.annotate import annotate
from pyjschema.draft_2019_09 import build_validator

from .referencing import _attach_base_URIs, _generate_context, _resolve_references
