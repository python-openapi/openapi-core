FastAPI
=========

This section describes integration with `FastAPI <https://fastapi.tiangolo.com>`__  ASGI framework.

.. note::

    FastAPI also provides OpenAPI support. The main difference is that, unlike FastAPI's code-first approach, OpenAPI-core allows you to laverage your existing specification that alligns with API-First approach. You can read more about API-first vs. code-first in the [Guide to API-first](https://www.postman.com/api-first/).

Middleware
----------

FastAPI can be integrated by `middleware <https://fastapi.tiangolo.com/tutorial/middleware/>`__ to apply OpenAPI validation to your entire application.

Add ``FastAPIOpenAPIMiddleware`` with OpenAPI object to your ``middleware`` list.

.. code-block:: python
  :emphasize-lines: 2,5

    from fastapi import FastAPI
    from openapi_core.contrib.fastapi.middlewares import FastAPIOpenAPIMiddleware

    app = FastAPI()
    app.add_middleware(FastAPIOpenAPIMiddleware, openapi=openapi)

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

    app = FastAPI()
    app.add_middleware(FastAPIOpenAPIMiddleware, openapi=openapi, response_cls=None)

Low level
---------

For low level integration see `Starlette <starlette.rst>`_ integration.
