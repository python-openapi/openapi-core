"""OpenAPI core schema shortcuts module"""
from jsonschema.validators import RefResolver
from openapi_spec_validator import default_handlers

from openapi_core.schema.specs.factories import SpecFactory


def create_spec(spec_dict, spec_url='', handlers=default_handlers):
    spec_resolver = RefResolver(
        spec_url, spec_dict, handlers=handlers)
    spec_factory = SpecFactory(spec_resolver)
    return spec_factory.create(spec_dict, spec_url=spec_url)
