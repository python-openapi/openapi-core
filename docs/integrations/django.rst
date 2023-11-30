Django
======

This section describes integration with `Django <https://www.djangoproject.com>`__ web framework.
The integration supports Django from version 3.0 and above.

Middleware
----------

Django can be integrated by `middleware <https://docs.djangoproject.com/en/5.0/topics/http/middleware/>`__ to apply OpenAPI validation to your entire application.

Add ``DjangoOpenAPIMiddleware`` to your ``MIDDLEWARE`` list and define ``OPENAPI``.

.. code-block:: python
  :emphasize-lines: 6,9

    # settings.py
    from openapi_core import OpenAPI

    MIDDLEWARE = [
       # ...
       'openapi_core.contrib.django.middlewares.DjangoOpenAPIMiddleware',
    ]

    OPENAPI = OpenAPI.from_dict(spec_dict)

After that all your requests and responses will be validated.

Also you have access to unmarshal result object with all unmarshalled request data through ``openapi`` attribute of request object.

.. code-block:: python

    from django.views import View

    class MyView(View):
       def get(self, request):
           # get parameters object with path, query, cookies and headers parameters
           unmarshalled_params = request.openapi.parameters
           # or specific location parameters
           unmarshalled_path_params = request.openapi.parameters.path

           # get body
           unmarshalled_body = request.openapi.body

           # get security data
           unmarshalled_security = request.openapi.security

Response validation
^^^^^^^^^^^^^^^^^^^

You can skip response validation process: by setting ``OPENAPI_RESPONSE_CLS`` to ``None``

.. code-block:: python
  :emphasize-lines: 10

    # settings.py
    from openapi_core import OpenAPI

    MIDDLEWARE = [
       # ...
       'openapi_core.contrib.django.middlewares.DjangoOpenAPIMiddleware',
    ]

    OPENAPI = OpenAPI.from_dict(spec_dict)
    OPENAPI_RESPONSE_CLS = None

Low level
---------

The integration defines classes useful for low level integration.

Request
^^^^^^^

Use ``DjangoOpenAPIRequest`` to create OpenAPI request from Django request:

.. code-block:: python

    from openapi_core.contrib.django import DjangoOpenAPIRequest

    class MyView(View):
       def get(self, request):
           openapi_request = DjangoOpenAPIRequest(request)
           openapi.validate_request(openapi_request)

Response
^^^^^^^^

Use ``DjangoOpenAPIResponse`` to create OpenAPI response from Django response:

.. code-block:: python

    from openapi_core.contrib.django import DjangoOpenAPIResponse

    class MyView(View):
       def get(self, request):
           response = JsonResponse({'hello': 'world'})
           openapi_request = DjangoOpenAPIRequest(request)
           openapi_response = DjangoOpenAPIResponse(response)
           openapi.validate_response(openapi_request, openapi_response)
           return response
