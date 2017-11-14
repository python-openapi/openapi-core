"""OpenAPI core module"""
from openapi_core.shortcuts import (
    create_spec, validate_parameters, validate_body,
)

__author__ = 'Artur Maciąg'
__email__ = 'maciag.artur@gmail.com'
__version__ = '0.4.0'
__url__ = 'https://github.com/p1c2u/openapi-core'
__license__ = 'BSD 3-Clause License'

__all__ = ['create_spec', 'validate_parameters', 'validate_body']
