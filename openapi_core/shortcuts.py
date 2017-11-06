"""OpenAPI core shortcuts module"""
from jsonschema.validators import RefResolver
from openapi_spec_validator.validators import Dereferencer
from openapi_spec_validator import default_handlers

from openapi_core.exceptions import OpenAPIParameterError, OpenAPIBodyError
from openapi_core.specs import SpecFactory
from openapi_core.validators import RequestValidator, ResponseValidator
from openapi_core.wrappers import FlaskOpenAPIRequest, FlaskOpenAPIResponse


def create_spec(spec_dict, spec_url=''):
    spec_resolver = RefResolver(
        spec_url, spec_dict, handlers=default_handlers)
    dereferencer = Dereferencer(spec_resolver)
    spec_factory = SpecFactory(dereferencer)
    return spec_factory.create(spec_dict, spec_url=spec_url)


def validate_parameters(spec, request, wrapper_class=FlaskOpenAPIRequest):
    if wrapper_class:
        request = wrapper_class(request)

    validator = RequestValidator(spec)
    result = validator.validate(request)
    try:
        result.raise_for_errors()
    except OpenAPIBodyError:
        return result.parameters
    else:
        return result.parameters


def validate_body(spec, request, wrapper_class=FlaskOpenAPIRequest):
    if wrapper_class:
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
        request_wrapper_class=FlaskOpenAPIRequest,
        response_wrapper_class=FlaskOpenAPIResponse):
    if request_wrapper_class:
        request = request_wrapper_class(request)
    if response_wrapper_class:
        response = response_wrapper_class(response)

    validator = ResponseValidator(spec)
    result = validator.validate(request, response)

    result.raise_for_errors()

    return result.data
