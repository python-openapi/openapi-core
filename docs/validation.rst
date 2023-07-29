Validation
==========

Validation is a process to validate request/response data under a given schema defined in OpenAPI specification.

Additionally, openapi-core uses the ``format`` keyword to check if primitive types conform to defined formats.

Such valid formats can be forther unmarshalled (See :doc:`unmarshalling`).

Depends on the OpenAPI version, openapi-core comes with a set of built-in format validators such as: ``date``, ``date-time``, ``binary``, ``uuid`` or ``byte``.

You can also define your own format validators (See :doc:`customizations`).

Request validation
------------------

Use ``validate_request`` function to validate request data against a given spec. By default, OpenAPI spec version is detected:

.. code-block:: python

    from openapi_core import validate_request

    # raises error if request is invalid
    validate_request(request, spec=spec)

Request object should implement OpenAPI Request protocol (See :doc:`integrations`).

.. note::

    Webhooks feature is part of OpenAPI v3.1 only

Use the same function to validate webhook request data against a given spec.

.. code-block:: python

    # raises error if request is invalid
    validate_request(webhook_request, spec=spec)

Webhook request object should implement OpenAPI WebhookRequest protocol (See :doc:`integrations`).

In order to explicitly validate and unmarshal a:

* OpenAPI 3.0 spec, import ``V30RequestValidator``
* OpenAPI 3.1 spec, import ``V31RequestValidator`` or ``V31WebhookRequestValidator``

.. code-block:: python
  :emphasize-lines: 1,6

    from openapi_core import V31RequestValidator

    validate_request(
       request, response,
       spec=spec,
       cls=V31RequestValidator,
    )

You can also explicitly import ``V3RequestValidator`` which is a shortcut to the latest OpenAPI v3 version.

Response validation
-------------------

Use ``validate_response`` function to validate response data against a given spec. By default, OpenAPI spec version is detected:

.. code-block:: python

    from openapi_core import validate_response

    # raises error if response is invalid
    validate_response(request, response, spec=spec)

Response object should implement OpenAPI Response protocol  (See :doc:`integrations`).

.. note::

    Webhooks feature is part of OpenAPI v3.1 only

Use the same function to validate response data from webhook request against a given spec.

.. code-block:: python

    # raises error if request is invalid
    validate_response(webhook_request, response, spec=spec)

In order to explicitly validate a:

* OpenAPI 3.0 spec, import ``V30ResponseValidator`` 
* OpenAPI 3.1 spec, import ``V31ResponseValidator`` or ``V31WebhookResponseValidator`` 

.. code-block:: python
  :emphasize-lines: 1,6

    from openapi_core import V31ResponseValidator

    validate_response(
       request, response,
       spec=spec,
       cls=V31ResponseValidator,
    )

You can also explicitly import ``V3ResponseValidator``  which is a shortcut to the latest OpenAPI v3 version.
