"""OpenAPI core shortcuts module"""
from jsonschema.validators import RefResolver
from openapi_spec_validator.validators import Dereferencer
from openapi_spec_validator import default_handlers

from openapi_core.specs import SpecFactory


def create_spec(spec_dict, spec_url=''):
    spec_resolver = RefResolver(
        spec_url, spec_dict, handlers=default_handlers)
    dereferencer = Dereferencer(spec_resolver)
    spec_factory = SpecFactory(dereferencer)
    return spec_factory.create(spec_dict, spec_url=spec_url)
