Validation
==========

Validation is a process to validate request/response data under a given schema defined in OpenAPI specification.

Additionally, openapi-core uses the ``format`` keyword to check if primitive types conform to defined formats.

Such valid formats can be forther unmarshalled (See :doc:`unmarshalling`).

Depends on the OpenAPI version, openapi-core comes with a set of built-in format validators such as: ``date``, ``date-time``, ``binary``, ``uuid`` or ``byte``.

You can also define your own format validators (See :doc:`customizations/extra_format_validators`).

Request validation
------------------

Use ``validate_request`` method to validate request data against a given spec. By default, OpenAPI spec version is detected:

.. code-block:: python

    # raises error if request is invalid
    openapi.validate_request(request)

Request object should implement OpenAPI Request protocol (See :doc:`integrations/index`).

.. note::

    Webhooks feature is part of OpenAPI v3.1 only

Use the same method to validate webhook request data against a given spec.

.. code-block:: python

    # raises error if request is invalid
    openapi.validate_request(webhook_request)

Webhook request object should implement OpenAPI WebhookRequest protocol (See :doc:`integrations/index`).

You can also define your own request validator (See :doc:`customizations/request_validator_cls`).

Response validation
-------------------

Use ``validate_response`` function to validate response data against a given spec. By default, OpenAPI spec version is detected:

.. code-block:: python

    from openapi_core import validate_response

    # raises error if response is invalid
    openapi.validate_response(request, response)

Response object should implement OpenAPI Response protocol  (See :doc:`integrations/index`).

.. note::

    Webhooks feature is part of OpenAPI v3.1 only

Use the same function to validate response data from webhook request against a given spec.

.. code-block:: python

    # raises error if request is invalid
    openapi.validate_response(webhook_request, response)

You can also define your own response validator (See :doc:`customizations/response_validator_cls`).
