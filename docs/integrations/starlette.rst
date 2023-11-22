Starlette
=========

This section describes integration with `Starlette <https://www.starlette.io>`__  ASGI framework.

Middleware
----------

Starlette can be integrated by middleware. Add ``StarletteOpenAPIMiddleware`` with ``spec`` to your ``middleware`` list.

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

After that you have access to unmarshal result object with all validated request data from endpoint through ``openapi`` key of request's scope directory.

.. code-block:: python

    async def get_endpoint(req):
       # get parameters object with path, query, cookies and headers parameters
       validated_params = req.scope["openapi"].parameters
       # or specific location parameters
       validated_path_params = req.scope["openapi"].parameters.path

       # get body
       validated_body = req.scope["openapi"].body

       # get security data
       validated_security = req.scope["openapi"].security

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

You can use ``StarletteOpenAPIRequest`` as a Starlette request factory:

.. code-block:: python

    from openapi_core.contrib.starlette import StarletteOpenAPIRequest

    openapi_request = StarletteOpenAPIRequest(starlette_request)
    result = openapi.unmarshal_request(openapi_request)

You can use ``StarletteOpenAPIResponse`` as a Starlette response factory:

.. code-block:: python

    from openapi_core.contrib.starlette import StarletteOpenAPIResponse

    openapi_response = StarletteOpenAPIResponse(starlette_response)
    result = openapi.unmarshal_response(openapi_request, openapi_response)
