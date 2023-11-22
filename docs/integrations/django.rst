Django
======

This section describes integration with `Django <https://www.djangoproject.com>`__ web framework.
The integration supports Django from version 3.0 and above.

Middleware
----------

Django can be integrated by middleware. Add ``DjangoOpenAPIMiddleware`` to your ``MIDDLEWARE`` list and define ``OPENAPI``.

.. code-block:: python
  :emphasize-lines: 6,9

    # settings.py
    from openapi_core import OpenAPI

    MIDDLEWARE = [
       # ...
       'openapi_core.contrib.django.middlewares.DjangoOpenAPIMiddleware',
    ]

    OPENAPI = OpenAPI.from_dict(spec_dict)

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

After that you have access to unmarshal result object with all validated request data from Django view through request object.

.. code-block:: python

    from django.views import View

    class MyView(View):
       def get(self, req):
           # get parameters object with path, query, cookies and headers parameters
           validated_params = req.openapi.parameters
           # or specific location parameters
           validated_path_params = req.openapi.parameters.path

           # get body
           validated_body = req.openapi.body

           # get security data
           validated_security = req.openapi.security

Low level
---------

You can use ``DjangoOpenAPIRequest`` as a Django request factory:

.. code-block:: python

    from openapi_core.contrib.django import DjangoOpenAPIRequest

    openapi_request = DjangoOpenAPIRequest(django_request)
    result = openapi.unmarshal_request(openapi_request)

You can use ``DjangoOpenAPIResponse`` as a Django response factory:

.. code-block:: python

    from openapi_core.contrib.django import DjangoOpenAPIResponse

    openapi_response = DjangoOpenAPIResponse(django_response)
    result = openapi.unmarshal_response(openapi_request, openapi_response)

