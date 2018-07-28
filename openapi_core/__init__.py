# -*- coding: utf-8 -*-

"""Python 2.7 backward compatibility"""
import openapi_core._python27_patch

"""OpenAPI core module"""
from openapi_core.shortcuts import (
    create_spec, validate_parameters, validate_body, validate_data,
)

__author__ = 'Artur Maciąg'
__email__ = 'maciag.artur@gmail.com'
__version__ = '0.5.0'
__url__ = 'https://github.com/p1c2u/openapi-core'
__license__ = 'BSD 3-Clause License'

__all__ = [
    'create_spec', 'validate_parameters', 'validate_body', 'validate_data',
]
