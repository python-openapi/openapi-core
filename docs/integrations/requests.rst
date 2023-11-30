Requests
========

This section describes integration with `Requests <https://requests.readthedocs.io>`__ library.

Low level
---------

The integration defines classes useful for low level integration.

Request
^^^^^^^

Use ``RequestsOpenAPIRequest`` to create OpenAPI request from Requests request:

.. code-block:: python

    from openapi_core.contrib.requests import RequestsOpenAPIRequest

    request = Request('POST', url, data=data, headers=headers)
    openapi_request = RequestsOpenAPIRequest(request)
    openapi.validate_request(openapi_request)

Webhook request
^^^^^^^^^^^^^^^

Use ``RequestsOpenAPIWebhookRequest`` to create OpenAPI webhook request from Requests request:

.. code-block:: python

    from openapi_core.contrib.requests import RequestsOpenAPIWebhookRequest

    request = Request('POST', url, data=data, headers=headers)
    openapi_webhook_request = RequestsOpenAPIWebhookRequest(request, "my_webhook")
    openapi.validate_request(openapi_webhook_request)

Response
^^^^^^^^

Use ``RequestsOpenAPIResponse`` to create OpenAPI response from Requests response:

.. code-block:: python

    from openapi_core.contrib.requests import RequestsOpenAPIResponse

    session = Session()
    request = Request('POST', url, data=data, headers=headers)
    prepped = session.prepare_request(req)
    response = session,send(prepped)
    openapi_request = RequestsOpenAPIRequest(request)
    openapi_response = RequestsOpenAPIResponse(response)
    openapi.validate_response(openapi_request, openapi_response)
