************
openapi-core
************

.. image:: https://img.shields.io/pypi/v/openapi-core.svg
     :target: https://pypi.python.org/pypi/openapi-core
.. image:: https://travis-ci.org/p1c2u/openapi-core.svg?branch=master
     :target: https://travis-ci.org/p1c2u/openapi-core
.. image:: https://img.shields.io/codecov/c/github/p1c2u/openapi-core/master.svg?style=flat
     :target: https://codecov.io/github/p1c2u/openapi-core?branch=master
.. image:: https://img.shields.io/pypi/pyversions/openapi-core.svg
     :target: https://pypi.python.org/pypi/openapi-core
.. image:: https://img.shields.io/pypi/format/openapi-core.svg
     :target: https://pypi.python.org/pypi/openapi-core
.. image:: https://img.shields.io/pypi/status/openapi-core.svg
     :target: https://pypi.python.org/pypi/openapi-core

About
#####

Openapi-core is a Python library that adds client-side and server-side support
for the `OpenAPI Specification v3.0.0 <https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md>`__.

Installation
############

Recommended way (via pip):

::

    $ pip install openapi-core

Alternatively you can download the code and install from the repository:

.. code-block:: bash

   $ pip install -e git+https://github.com/p1c2u/openapi-core.git#egg=openapi_core


Usage
#####

Firstly create your specification:

.. code-block:: python

   from openapi_core import create_spec

   spec = create_spec(spec_dict)

Request
*******

Now you can use it to validate requests

.. code-block:: python

   from openapi_core.shortcuts import RequestValidator

   validator = RequestValidator(spec)
   result = validator.validate(request)

   # raise errors if request invalid
   result.raise_for_errors()

   # get list of errors
   errors = result.errors

and unmarshal request data from validation result

.. code-block:: python

   # get parameters object with path, query, cookies and headers parameters
   validated_params = result.parameters
   # or specific parameters
   validated_path_params = result.parameters.path

   # get body
   validated_body = result.body

or use shortcuts for simple validation

.. code-block:: python

   from openapi_core import validate_parameters, validate_body

   validated_params = validate_parameters(spec, request)
   validated_body = validate_body(spec, request)

Request object should be instance of OpenAPIRequest class (See `Integrations`_).

Response
********

You can also validate responses

.. code-block:: python

   from openapi_core.shortcuts import ResponseValidator

   validator = ResponseValidator(spec)
   result = validator.validate(request, response)

   # raise errors if response invalid
   result.raise_for_errors()

   # get list of errors
   errors = result.errors

and unmarshal response data from validation result

.. code-block:: python

   # get headers
   validated_headers = result.headers

   # get data
   validated_data = result.data

or use shortcuts for simple validation

.. code-block:: python

   from openapi_core import validate_data

   validated_data = validate_data(spec, request, response)

Response object should be instance of OpenAPIResponse class (See `Integrations`_).


Integrations
############

Django
******

You can use DjangoOpenAPIRequest a Django request factory:

.. code-block:: python

   from openapi_core.shortcuts import RequestValidator
   from openapi_core.contrib.django import DjangoOpenAPIRequest

   openapi_request = DjangoOpenAPIRequest(django_request)
   validator = RequestValidator(spec)
   result = validator.validate(openapi_request)

or simply specify request factory for shortcuts

.. code-block:: python

   from openapi_core import validate_parameters, validate_body

   validated_params = validate_parameters(
       spec, request, request_factory=DjangoOpenAPIRequest)
   validated_body = validate_body(
       spec, request, request_factory=DjangoOpenAPIRequest)

You can use DjangoOpenAPIResponse as a Django response factory:

.. code-block:: python

   from openapi_core.shortcuts import ResponseValidator
   from openapi_core.contrib.django import DjangoOpenAPIResponse

   openapi_response = DjangoOpenAPIResponse(django_response)
   validator = ResponseValidator(spec)
   result = validator.validate(openapi_request, openapi_response)

or simply specify response factory for shortcuts

.. code-block:: python

   from openapi_core import validate_parameters, validate_body

   validated_data = validate_data(
       spec, request, response,
       request_factory=DjangoOpenAPIRequest,
       response_factory=DjangoOpenAPIResponse)

Flask
*****

You can use FlaskOpenAPIRequest a Flask/Werkzeug request factory:

.. code-block:: python

   from openapi_core.shortcuts import RequestValidator
   from openapi_core.contrib.flask import FlaskOpenAPIRequest

   openapi_request = FlaskOpenAPIRequest(flask_request)
   validator = RequestValidator(spec)
   result = validator.validate(openapi_request)

or simply specify request factory for shortcuts

.. code-block:: python

   from openapi_core import validate_parameters, validate_body

   validated_params = validate_parameters(
       spec, request, request_factory=FlaskOpenAPIRequest)
   validated_body = validate_body(
       spec, request, request_factory=FlaskOpenAPIRequest)

You can use FlaskOpenAPIResponse as a Flask/Werkzeug response factory:

.. code-block:: python

   from openapi_core.shortcuts import ResponseValidator
   from openapi_core.contrib.flask import FlaskOpenAPIResponse

   openapi_response = FlaskOpenAPIResponse(flask_response)
   validator = ResponseValidator(spec)
   result = validator.validate(openapi_request, openapi_response)

or simply specify response factory for shortcuts

.. code-block:: python

   from openapi_core import validate_parameters, validate_body

   validated_data = validate_data(
       spec, request, response,
       request_factory=FlaskOpenAPIRequest,
       response_factory=FlaskOpenAPIResponse)

Pyramid
*******

See `pyramid_openapi3  <https://github.com/niteoweb/pyramid_openapi3>`_ project.

Related projects
################
* `openapi-spec-validator <https://github.com/p1c2u/openapi-spec-validator>`__
* `pyramid_openapi3 <https://github.com/niteoweb/pyramid_openapi3>`__
