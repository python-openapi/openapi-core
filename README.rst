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
for the `OpenAPI v3.0 <https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.3.md>`__
and `OpenAPI v3.1 <https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md>`__ specification.

Key features
************

* **Validation** of requests and responses
* Schema **casting** and **unmarshalling**
* Media type and parameters **deserialization**
* **Security** providers (API keys, Cookie, Basic and Bearer HTTP authentications)
* Custom **deserializers** and **formats**
* **Integration** with libraries and frameworks


Documentation
#############

Check documentation to see more details about the features. All documentation is in the "docs" directory and online at `openapi-core.readthedocs.io <https://openapi-core.readthedocs.io>`__


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

Firstly create your specification object.

.. code-block:: python

   from openapi_core import Spec

   spec = Spec.from_file_path('openapi.json')

Now you can use it to validate against requests and/or responses. 

Request
*******

Use ``validate_request`` function to validate request against a given spec.

.. code-block:: python

   from openapi_core import validate_request

   # raise error if request is invalid
   result = validate_request(request, spec=spec)

Request object should implement OpenAPI Request protocol (See `Integrations <https://openapi-core.readthedocs.io/en/latest/integrations.html>`__).

(For OpenAPI v3.1) Use the same function to validate webhook request against a given spec.

.. code-block:: python

   # raise error if request is invalid
   result = validate_request(webhook_request, spec=spec)

Webhook request object should implement OpenAPI WebhookRequest protocol (See `Integrations <https://openapi-core.readthedocs.io/en/latest/integrations.html>`__).

Retrieve request data from validation result

.. code-block:: python

   # get parameters object with path, query, cookies and headers parameters
   validated_params = result.parameters
   # or specific parameters
   validated_path_params = result.parameters.path

   # get body
   validated_body = result.body

   # get security data
   validated_security = result.security

Response
********

Use ``validate_response`` function to validate response against a given spec.

.. code-block:: python

   from openapi_core import validate_response

   # raise error if response is invalid
   result = validate_response(request, response, spec=spec)

Response object should implement OpenAPI Response protocol (See `Integrations <https://openapi-core.readthedocs.io/en/latest/integrations.html>`__).

(For OpenAPI v3.1) Use the same function to validate response from webhook request against a given spec.

.. code-block:: python

   # raise error if request is invalid
   result = validate_response(webhook_request, response, spec=spec)

Retrieve response data from validation result

.. code-block:: python

   # get headers
   validated_headers = result.headers

   # get data
   validated_data = result.data

In order to explicitly validate a:

* OpenAPI 3.0 spec, import ``V30RequestValidator`` or ``V30ResponseValidator`` 
* OpenAPI 3.1 spec, import ``V31RequestValidator`` or ``V31ResponseValidator`` or ``V31WebhookRequestValidator`` or ``V31WebhookResponseValidator`` 

.. code:: python

   from openapi_core import V31ResponseValidator

   result = validate_response(request, response, spec=spec, cls=V31ResponseValidator)

You can also explicitly import ``V3RequestValidator`` or ``V3ResponseValidator``  which is a shortcut to the latest v3 release.

Related projects
################
* `bottle-openapi-3 <https://github.com/cope-systems/bottle-openapi-3>`__
   OpenAPI 3.0 Support for the Bottle Web Framework
* `openapi-spec-validator <https://github.com/p1c2u/openapi-spec-validator>`__
   Python library that validates OpenAPI Specs against the OpenAPI 2.0 (aka Swagger) and OpenAPI 3.0 specification
* `openapi-schema-validator <https://github.com/p1c2u/openapi-schema-validator>`__
   Python library that validates schema against the OpenAPI Schema Specification v3.0.
* `pyramid_openapi3 <https://github.com/niteoweb/pyramid_openapi3>`__
   Pyramid addon for OpenAPI3 validation of requests and responses.
* `tornado-openapi3 <https://github.com/correl/tornado-openapi3>`__
   Tornado OpenAPI 3 request and response validation library.
