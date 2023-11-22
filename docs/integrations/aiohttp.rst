aiohttp.web
===========

This section describes integration with `aiohttp.web <https://docs.aiohttp.org/en/stable/web.html>`__ framework.

Low level
---------

You can use ``AIOHTTPOpenAPIWebRequest`` as an aiohttp request factory:

.. code-block:: python

    from openapi_core.contrib.aiohttp import AIOHTTPOpenAPIWebRequest

    request_body = await aiohttp_request.text()
    openapi_request = AIOHTTPOpenAPIWebRequest(aiohttp_request, body=request_body)
    result = openapi.unmarshal_request(openapi_request)

You can use ``AIOHTTPOpenAPIWebRequest`` as an aiohttp response factory:

.. code-block:: python

    from openapi_core.contrib.starlette import AIOHTTPOpenAPIWebRequest

    openapi_response = StarletteOpenAPIResponse(aiohttp_response)
    result = openapi.unmarshal_response(openapi_request, openapi_response)
