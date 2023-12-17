Starlette
=========

This section describes integration with `Starlette <https://www.starlette.io>`__  ASGI framework.

Middleware
----------

Starlette can be integrated by `middleware <https://www.starlette.io/middleware/>`__ to apply OpenAPI validation to your entire application.

Add ``StarletteOpenAPIMiddleware`` with OpenAPI object to your ``middleware`` list.

.. code-block:: python
  :emphasize-lines: 1,6

    from openapi_core.contrib.starlette.middlewares import StarletteOpenAPIMiddleware
    from starlette.applications import Starlette
    from starlette.middleware import Middleware

    middleware = [
        Middleware(StarletteOpenAPIMiddleware, openapi=openapi),
    ]

    app = Starlette(
        # ...
        middleware=middleware,
    )

After that all your requests and responses will be validated.

Also you have access to unmarshal result object with all unmarshalled request data through ``openapi`` scope of request object.

.. code-block:: python

    async def homepage(request):
       # get parameters object with path, query, cookies and headers parameters
       unmarshalled_params = request.scope["openapi"].parameters
       # or specific location parameters
       unmarshalled_path_params = request.scope["openapi"].parameters.path

       # get body
       unmarshalled_body = request.scope["openapi"].body

       # get security data
       unmarshalled_security = request.scope["openapi"].security

Response validation
^^^^^^^^^^^^^^^^^^^

You can skip response validation process: by setting ``response_cls`` to ``None``

.. code-block:: python
  :emphasize-lines: 2

    middleware = [
        Middleware(StarletteOpenAPIMiddleware, openapi=openapi, response_cls=None),
    ]

    app = Starlette(
        # ...
        middleware=middleware,
    )

Low level
---------

The integration defines classes useful for low level integration.

Request
^^^^^^^

Use ``StarletteOpenAPIRequest`` to create OpenAPI request from Starlette request:

.. code-block:: python

    from openapi_core.contrib.starlette import StarletteOpenAPIRequest

    async def homepage(request):
        openapi_request = StarletteOpenAPIRequest(request)
        result = openapi.unmarshal_request(openapi_request)
        return JSONResponse({'hello': 'world'})

Response
^^^^^^^^

Use ``StarletteOpenAPIResponse`` to create OpenAPI response from Starlette response:

.. code-block:: python

    from openapi_core.contrib.starlette import StarletteOpenAPIResponse

    async def homepage(request):
        response = JSONResponse({'hello': 'world'})
        openapi_request = StarletteOpenAPIRequest(request)
        openapi_response = StarletteOpenAPIResponse(response)
        openapi.validate_response(openapi_request, openapi_response)
        return response
