from typing import Optional

from dictpath.paths import AccessorPath

from openapi_core.spec.accessors import SpecAccessor
from openapi_spec_validator.validators import Dereferencer

SPEC_SEPARATOR = '#'


class SpecPath(AccessorPath):

    @classmethod
    def from_spec(
        cls,
        spec_dict: dict,
        dereferencer: Optional[Dereferencer] = None,
        *args, **kwargs,
    ) -> 'SpecPath':
        separator = kwargs.pop('separator', SPEC_SEPARATOR)
        accessor = SpecAccessor(spec_dict, dereferencer)
        return cls(accessor, *args, separator=separator)
