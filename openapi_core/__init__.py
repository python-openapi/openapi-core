"""OpenAPI core module"""
from openapi_core.shortcuts import create_spec
from openapi_core.wrappers import RequestParametersFactory, RequestBodyFactory

__author__ = 'Artur Maciąg'
__email__ = 'maciag.artur@gmail.com'
__version__ = '0.1.4'
__url__ = 'https://github.com/p1c2u/openapi-core'
__license__ = 'BSD 3-Clause License'

__all__ = ['create_spec', 'request_parameters_factory', 'request_body_factory']

request_parameters_factory = RequestParametersFactory()
request_body_factory = RequestBodyFactory()
