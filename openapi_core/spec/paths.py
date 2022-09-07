from jsonschema.validators import RefResolver
from openapi_spec_validator import default_handlers
from openapi_spec_validator import openapi_v3_spec_validator
from openapi_spec_validator.validators import Dereferencer
from pathable.paths import AccessorPath

from openapi_core.spec.accessors import SpecAccessor

SPEC_SEPARATOR = "#"


class Spec(AccessorPath):
    @classmethod
    def from_dict(
        cls,
        data,
        *args,
        url="",
        ref_resolver_handlers=default_handlers,
        separator=SPEC_SEPARATOR,
    ):
        ref_resolver = RefResolver(url, data, handlers=ref_resolver_handlers)
        dereferencer = Dereferencer(ref_resolver)
        accessor = SpecAccessor(data, dereferencer)
        return cls(accessor, *args, separator=separator)

    @classmethod
    def create(
        cls,
        data,
        *args,
        url="",
        ref_resolver_handlers=default_handlers,
        separator=SPEC_SEPARATOR,
        validator=openapi_v3_spec_validator,
    ):
        if validator is not None:
            validator.validate(data, spec_url=url)

        return cls.from_dict(
            data,
            *args,
            url=url,
            ref_resolver_handlers=ref_resolver_handlers,
            separator=separator,
        )
