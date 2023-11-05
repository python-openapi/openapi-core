************
openapi-core
************

.. image:: https://img.shields.io/pypi/v/openapi-core.svg
     :target: https://pypi.python.org/pypi/openapi-core
.. image:: https://travis-ci.org/python-openapi/openapi-core.svg?branch=master
     :target: https://travis-ci.org/python-openapi/openapi-core
.. image:: https://img.shields.io/codecov/c/github/python-openapi/openapi-core/master.svg?style=flat
     :target: https://codecov.io/github/python-openapi/openapi-core?branch=master
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
############

* **Validation** and **unmarshalling** of request and response data (including webhooks)
* **Integration** with popular libraries (Requests, Werkzeug) and frameworks (Django, Falcon, Flask, Starlette)
* Customization with media type **deserializers** and format **unmarshallers**
* **Security** data providers (API keys, Cookie, Basic and Bearer HTTP authentications)


Documentation
#############

Check documentation to see more details about the features. All documentation is in the "docs" directory and online at `openapi-core.readthedocs.io <https://openapi-core.readthedocs.io>`__


Installation
############

Recommended way (via pip):

.. code-block:: console

    pip install openapi-core

Alternatively you can download the code and install from the repository:

.. code-block:: console

    pip install -e git+https://github.com/python-openapi/openapi-core.git#egg=openapi_core


First steps
###########

Firstly create your OpenAPI object.

.. code-block:: python

    from openapi_core import OpenAPI

    openapi = OpenAPI.from_file_path('openapi.json')

Now you can use it to validate and unmarshal against requests and/or responses. 

.. code-block:: python

    # raises error if request is invalid
    result = openapi.unmarshal_request(request)

Retrieve validated and unmarshalled request data

.. code-block:: python

    # get parameters
    path_params = result.parameters.path
    query_params = result.parameters.query
    cookies_params = result.parameters.cookies
    headers_params = result.parameters.headers
    # get body
    body = result.body
    # get security data
    security = result.security

Request object should implement OpenAPI Request protocol. Check `Integrations <https://openapi-core.readthedocs.io/en/latest/integrations.html>`__ to find officially supported implementations.

For more details read about `Unmarshalling <https://openapi-core.readthedocs.io/en/latest/unmarshalling.html>`__ process.

If you just want to validate your request/response data without unmarshalling, read about `Validation <https://openapi-core.readthedocs.io/en/latest/validation.html>`__ instead.


Related projects
################
* `openapi-spec-validator <https://github.com/python-openapi/openapi-spec-validator>`__
    Python library that validates OpenAPI Specs against the OpenAPI 2.0 (aka Swagger), OpenAPI 3.0 and OpenAPI 3.1 specification. The validator aims to check for full compliance with the Specification.
* `openapi-schema-validator <https://github.com/python-openapi/openapi-schema-validator>`__
    Python library that validates schema against the OpenAPI Schema Specification v3.0 and OpenAPI Schema Specification v3.1.
* `bottle-openapi-3 <https://github.com/cope-systems/bottle-openapi-3>`__
    OpenAPI 3.0 Support for the Bottle Web Framework
* `pyramid_openapi3 <https://github.com/niteoweb/pyramid_openapi3>`__
    Pyramid addon for OpenAPI3 validation of requests and responses.
* `tornado-openapi3 <https://github.com/correl/tornado-openapi3>`__
    Tornado OpenAPI 3 request and response validation library.


License
#######

The project is under the terms of BSD 3-Clause License.
