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

Firstly create your specification object. By default, OpenAPI spec version is detected:

.. code-block:: python

   from json import load
   from openapi_core import Spec

   with open('openapi.json', 'r') as spec_file:
      spec_dict = load(spec_file)

   spec = Spec.create(spec_dict)

Request
*******

Now you can use it to validate against requests

.. code-block:: python

   from openapi_core import openapi_request_validator

   result = openapi_request_validator.validate(spec, request)

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

   # get security data
   validated_security = result.security

Request object should implement OpenAPI Request protocol (See `Integrations <https://openapi-core.readthedocs.io/en/latest/integrations.html>`__).

Response
********

You can also validate against responses

.. code-block:: python

   from openapi_core import openapi_response_validator

   result = openapi_response_validator.validate(spec, request, response)

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

Response object should implement OpenAPI Response protocol (See `Integrations <https://openapi-core.readthedocs.io/en/latest/integrations.html>`__).

In order to explicitly validate a:

* OpenAPI 3.0 spec, import ``openapi_v30_request_validator`` or ``openapi_v30_response_validator`` 
* OpenAPI 3.1 spec, import ``openapi_v31_request_validator`` or ``openapi_v31_response_validator`` 

.. code:: python

   from openapi_core import openapi_v31_response_validator

   result = openapi_v31_response_validator.validate(spec, request, response)

You can also explicitly import ``openapi_v3_request_validator`` or ``openapi_v3_response_validator``  which is a shortcut to the latest v3 release.

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
