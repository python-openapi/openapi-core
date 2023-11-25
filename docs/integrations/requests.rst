Requests
========

This section describes integration with `Requests <https://requests.readthedocs.io>`__ library.

Low level
---------

You can use ``RequestsOpenAPIRequest`` as a Requests request factory:

.. code-block:: python

    from openapi_core.contrib.requests import RequestsOpenAPIRequest

    openapi_request = RequestsOpenAPIRequest(requests_request)
    result = openapi.unmarshal_request(openapi_request)

You can use ``RequestsOpenAPIResponse`` as a Requests response factory:

.. code-block:: python

    from openapi_core.contrib.requests import RequestsOpenAPIResponse

    openapi_response = RequestsOpenAPIResponse(requests_response)
    result = openapi.unmarshal_response(openapi_request, openapi_response)


You can use ``RequestsOpenAPIWebhookRequest`` as a Requests webhook request factory:

.. code-block:: python

    from openapi_core.contrib.requests import RequestsOpenAPIWebhookRequest

    openapi_webhook_request = RequestsOpenAPIWebhookRequest(requests_request, "my_webhook")
    result = openapi.unmarshal_request(openapi_webhook_request)
