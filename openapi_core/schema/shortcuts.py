"""OpenAPI core schema shortcuts module"""
from jsonschema.validators import RefResolver
from openapi_spec_validator import (
    default_handlers, openapi_v3_spec_validator,
)
from openapi_spec_validator.validators import Dereferencer

from openapi_core.schema.specs.factories import SpecFactory


def create_spec(
    spec_dict, spec_url='', handlers=default_handlers,
    validate_spec=True,
):
    if validate_spec:
        openapi_v3_spec_validator.validate(spec_dict, spec_url=spec_url)

    spec_resolver = RefResolver(
        spec_url, spec_dict, handlers=handlers)
    dereferencer = Dereferencer(spec_resolver)
    from openapi_core.spec.paths import SpecPath
    return SpecPath.from_spec(spec_dict, dereferencer)
    spec_factory = SpecFactory(spec_resolver)
    return spec_factory.create(spec_dict, spec_url=spec_url)
