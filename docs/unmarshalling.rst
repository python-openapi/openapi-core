Unmarshalling
=============

Unmarshalling is the process of converting a primitive schema type of value into a higher-level object based on a ``format`` keyword. All request/response data, that can be described by a schema in OpenAPI specification, can be unmarshalled.

Unmarshallers firstly validate data against the provided schema (See :doc:`validation`).

Openapi-core comes with a set of built-in format unmarshallers:

* ``date`` - converts string into a date object,
* ``date-time`` - converts string into a datetime object,
* ``binary`` - converts string into a byte object,
* ``uuid`` - converts string into an UUID object,
* ``byte`` - decodes Base64-encoded string.

You can also define your own format unmarshallers (See :doc:`customizations`).

Request unmarshalling
---------------------

Use ``unmarshal_request`` function to validate and unmarshal request data against a given spec. By default, OpenAPI spec version is detected:

.. code-block:: python

    from openapi_core import unmarshal_request

    # raises error if request is invalid
    result = unmarshal_request(request, spec=spec)

Request object should implement OpenAPI Request protocol (See :doc:`integrations`).

.. note::

    Webhooks feature is part of OpenAPI v3.1 only

Use the same function to validate and unmarshal webhook request data against a given spec.

.. code-block:: python

    # raises error if request is invalid
    result = unmarshal_request(webhook_request, spec=spec)

Webhook request object should implement OpenAPI WebhookRequest protocol (See :doc:`integrations`).

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

In order to explicitly validate and unmarshal a:

* OpenAPI 3.0 spec, import ``V30RequestUnmarshaller``
* OpenAPI 3.1 spec, import ``V31RequestUnmarshaller`` or ``V31WebhookRequestUnmarshaller``

.. code-block:: python
  :emphasize-lines: 1,6

    from openapi_core import V31RequestUnmarshaller

    result = unmarshal_request(
       request, response,
       spec=spec,
       cls=V31RequestUnmarshaller,
    )

You can also explicitly import ``V3RequestUnmarshaller`` which is a shortcut to the latest OpenAPI v3 version.

Response unmarshalling
----------------------

Use ``unmarshal_response`` function to validate and unmarshal response data against a given spec. By default, OpenAPI spec version is detected:

.. code-block:: python

    from openapi_core import unmarshal_response

    # raises error if response is invalid
    result = unmarshal_response(request, response, spec=spec)

Response object should implement OpenAPI Response protocol  (See :doc:`integrations`).

.. note::

    Webhooks feature is part of OpenAPI v3.1 only

Use the same function to validate and unmarshal response data from webhook request against a given spec.

.. code-block:: python

    # raises error if request is invalid
    result = unmarshal_response(webhook_request, response, spec=spec)

Retrieve validated and unmarshalled response data

.. code-block:: python

    # get headers
    headers = result.headers
    # get data
    data = result.data

In order to explicitly validate and unmarshal a:

* OpenAPI 3.0 spec, import ``V30ResponseUnmarshaller`` 
* OpenAPI 3.1 spec, import ``V31ResponseUnmarshaller`` or ``V31WebhookResponseUnmarshaller`` 

.. code-block:: python
  :emphasize-lines: 1,6

    from openapi_core import V31ResponseUnmarshaller

    result = unmarshal_response(
       request, response,
       spec=spec,
       cls=V31ResponseUnmarshaller,
    )

You can also explicitly import ``V3ResponseUnmarshaller``  which is a shortcut to the latest OpenAPI v3 version.
