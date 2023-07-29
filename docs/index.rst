openapi-core
============

.. toctree::
    :hidden:
    :maxdepth: 2

    unmarshalling
    validation
    integrations
    customizations
    security
    extensions
    contributing

Openapi-core is a Python library that adds client-side and server-side support
for the `OpenAPI v3.0 <https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.3.md>`__
and `OpenAPI v3.1 <https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md>`__ specification.

Key features
------------

* :doc:`validation` and :doc:`unmarshalling <unmarshalling>` of request and response data (including webhooks)
* :doc:`Integrations <integrations>` with popular libraries (Requests, Werkzeug) and frameworks (Django, Falcon, Flask, Starlette)
* :doc:`Customization <customizations>` with **media type deserializers** and **format unmarshallers**
* :doc:`Security <security>` data providers (API keys, Cookie, Basic and Bearer HTTP authentications)

Installation
------------

.. md-tab-set::

    .. md-tab-item:: Pip + PyPI (recommented)

      .. code-block:: console

         pip install openapi-core

    .. md-tab-item:: Pip + the source

      .. code-block:: console

         pip install -e git+https://github.com/python-openapi/openapi-core.git#egg=openapi_core

First steps
-----------

Firstly create your specification object.

.. code-block:: python

    from openapi_core import Spec

    spec = Spec.from_file_path('openapi.json')

Now you can use it to validate and unmarshal your requests and/or responses. 

.. code-block:: python

    from openapi_core import unmarshal_request

    # raises error if request is invalid
    result = unmarshal_request(request, spec=spec)

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

Request object should implement OpenAPI Request protocol. Check :doc:`integrations` to find oficially supported implementations.

For more details read about :doc:`unmarshalling` process.

If you just want to validate your request/response data without unmarshalling, read about :doc:`validation` instead.

Related projects
----------------

* `openapi-spec-validator <https://github.com/python-openapi/openapi-spec-validator>`__
    Python library that validates OpenAPI Specs against the OpenAPI 2.0 (aka Swagger), OpenAPI 3.0 and OpenAPI 3.1 specification. The validator aims to check for full compliance with the Specification.
* `openapi-schema-validator <https://github.com/python-openapi/openapi-schema-validator>`__
    Python library that validates schema against the OpenAPI Schema Specification v3.0 and OpenAPI Schema Specification v3.1.

License
-------

The project is under the terms of BSD 3-Clause License.
