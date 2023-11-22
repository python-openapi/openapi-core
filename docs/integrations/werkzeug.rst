Werkzeug
========

This section describes integration with `Werkzeug <https://werkzeug.palletsprojects.com>`__ a WSGI web application library.

Low level
---------

The integration defines ``WerkzeugOpenAPIRequest`` and ``WerkzeugOpenAPIResponse`` classes that convert
Werkzeug requests and responses to OpenAPI ones.

.. md-tab-set::

    .. md-tab-item:: Request

      .. code-block:: python

         from openapi_core.contrib.werkzeug import WerkzeugOpenAPIRequest

         openapi_request = WerkzeugOpenAPIRequest(werkzeug_request)

         result = openapi.unmarshal_request(openapi_request)

    .. md-tab-item:: Response

      .. code-block:: python

         from openapi_core.contrib.werkzeug import WerkzeugOpenAPIRequest, WerkzeugOpenAPIResponse

         openapi_request = WerkzeugOpenAPIRequest(werkzeug_request)
         openapi_response = WerkzeugOpenAPIResponse(werkzeug_response)

         result = openapi.unmarshal_response(openapi_request, openapi_response)
