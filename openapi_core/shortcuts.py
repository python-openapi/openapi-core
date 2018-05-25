"""OpenAPI core shortcuts module"""
from jsonschema.validators import RefResolver
from openapi_spec_validator.validators import Dereferencer
from openapi_spec_validator import default_handlers

from openapi_core.schema.media_types.exceptions import OpenAPIMediaTypeError
from openapi_core.schema.parameters.exceptions import OpenAPIParameterError
from openapi_core.schema.request_bodies.exceptions import (
    OpenAPIRequestBodyError,
)
from openapi_core.schema.schemas.exceptions import OpenAPISchemaError
from openapi_core.schema.specs.factories import SpecFactory
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator


def create_spec(spec_dict, spec_url=''):
    spec_resolver = RefResolver(
        spec_url, spec_dict, handlers=default_handlers)
    dereferencer = Dereferencer(spec_resolver)
    spec_factory = SpecFactory(dereferencer)
    return spec_factory.create(spec_dict, spec_url=spec_url)


def validate_parameters(spec, request, wrapper_class=None):
    if wrapper_class is not None:
        request = wrapper_class(request)

    validator = RequestValidator(spec)
    result = validator.validate(request)

    try:
        result.raise_for_errors()
    except (
            OpenAPIRequestBodyError, OpenAPIMediaTypeError,
            OpenAPISchemaError,
    ):
        return result.parameters
    else:
        return result.parameters


def validate_body(spec, request, wrapper_class=None):
    if wrapper_class is not None:
        request = wrapper_class(request)

    validator = RequestValidator(spec)
    result = validator.validate(request)

    try:
        result.raise_for_errors()
    except OpenAPIParameterError:
        return result.body
    else:
        return result.body


def validate_data(
        spec, request, response,
        request_wrapper_class=None,
        response_wrapper_class=None):
    if request_wrapper_class is not None:
        request = request_wrapper_class(request)

    if response_wrapper_class is not None:
        response = response_wrapper_class(response)

    validator = ResponseValidator(spec)
    result = validator.validate(request, response)

    result.raise_for_errors()

    return result.data
