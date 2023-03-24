Integrations
============

Openapi-core integrates with your popular libraries and frameworks. Each integration offers different levels of integration that help validate and unmarshal your request and response data.

Amazon API Gateway
------------------

This section describes integration with `Amazon API Gateway <https://aws.amazon.com/api-gateway/>`__.

It is useful for:
 * `AWS Lambda integrations <https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html>`__ where Lambda functions handle events from API Gateway (Amazon API Gateway event format version 1.0 and 2.0).
 * `AWS Lambda function URLs <https://docs.aws.amazon.com/lambda/latest/dg/lambda-urls.html>`__ where Lambda functions handle events from dedicated HTTP(S) endpoint (Amazon API Gateway event format version 2.0).

Low level
~~~~~~~~~

You can use ``APIGatewayEventV2OpenAPIRequest`` as an API Gateway event (format version 2.0) request factory:

.. code-block:: python

   from openapi_core import unmarshal_request
   from openapi_core.contrib.aws import APIGatewayEventV2OpenAPIRequest

   openapi_request = APIGatewayEventV2OpenAPIRequest(event)
   result = unmarshal_request(openapi_request, spec=spec)

If you use format version 1.0, then import and use ``APIGatewayEventOpenAPIRequest`` as an API Gateway event (format version 1.0) request factory.

You can use ``APIGatewayEventV2ResponseOpenAPIResponse`` as an API Gateway event (format version 2.0) response factory:

.. code-block:: python

   from openapi_core import unmarshal_response
   from openapi_core.contrib.aws import APIGatewayEventV2ResponseOpenAPIResponse

   openapi_response = APIGatewayEventV2ResponseOpenAPIResponse(response)
   result = unmarshal_response(openapi_request, openapi_response, spec=spec)

If you use format version 1.0, then import and use ``APIGatewayEventResponseOpenAPIResponse`` as an API Gateway event (format version 1.0) response factory.

ANY method
~~~~~~~~~~

API Gateway have special ``ANY`` method that catches all HTTP methods. It's specified as `x-amazon-apigateway-any-method <https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-swagger-extensions-any-method.html>`__ OpenAPI extension. If you use the extension, you want to define ``path_finder_cls`` to be ``APIGatewayPathFinder``:

.. code-block:: python

   from openapi_core.contrib.aws import APIGatewayPathFinder

   result = unmarshal_response(
      openapi_request,
      openapi_response,
      spec=spec,
      path_finder_cls=APIGatewayPathFinder,
   )


Bottle
------

See `bottle-openapi-3 <https://github.com/cope-systems/bottle-openapi-3>`_ project.


Django
------

This section describes integration with `Django <https://www.djangoproject.com>`__ web framework.
The integration supports Django from version 3.0 and above.

Middleware
~~~~~~~~~~

Django can be integrated by middleware. Add ``DjangoOpenAPIMiddleware`` to your ``MIDDLEWARE`` list and define ``OPENAPI_SPEC``.

.. code-block:: python

   # settings.py
   from openapi_core import Spec

   MIDDLEWARE = [
       # ...
       'openapi_core.contrib.django.middlewares.DjangoOpenAPIMiddleware',
   ]

   OPENAPI_SPEC = Spec.from_dict(spec_dict)

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
~~~~~~~~~

You can use ``DjangoOpenAPIRequest`` as a Django request factory:

.. code-block:: python

   from openapi_core import unmarshal_request
   from openapi_core.contrib.django import DjangoOpenAPIRequest

   openapi_request = DjangoOpenAPIRequest(django_request)
   result = unmarshal_request(openapi_request, spec=spec)

You can use ``DjangoOpenAPIResponse`` as a Django response factory:

.. code-block:: python

   from openapi_core import unmarshal_response
   from openapi_core.contrib.django import DjangoOpenAPIResponse

   openapi_response = DjangoOpenAPIResponse(django_response)
   result = unmarshal_response(openapi_request, openapi_response, spec=spec)


Falcon
------

This section describes integration with `Falcon <https://falconframework.org>`__ web framework.
The integration supports Falcon from version 3.0 and above.

Middleware
~~~~~~~~~~

The Falcon API can be integrated by ``FalconOpenAPIMiddleware`` middleware.

.. code-block:: python

   from openapi_core.contrib.falcon.middlewares import FalconOpenAPIMiddleware

   openapi_middleware = FalconOpenAPIMiddleware.from_spec(spec)
   app = falcon.App(middleware=[openapi_middleware])

After that you will have access to validation result object with all validated request data from Falcon view through request context.

.. code-block:: python

   class ThingsResource:
       def on_get(self, req, resp):
           # get parameters object with path, query, cookies and headers parameters
           validated_params = req.context.openapi.parameters
           # or specific location parameters
           validated_path_params = req.context.openapi.parameters.path

           # get body
           validated_body = req.context.openapi.body

           # get security data
           validated_security = req.context.openapi.security

Low level
~~~~~~~~~

You can use ``FalconOpenAPIRequest`` as a Falcon request factory:

.. code-block:: python

   from openapi_core import unmarshal_request
   from openapi_core.contrib.falcon import FalconOpenAPIRequest

   openapi_request = FalconOpenAPIRequest(falcon_request)
   result = unmarshal_request(openapi_request, spec=spec)

You can use ``FalconOpenAPIResponse`` as a Falcon response factory:

.. code-block:: python

   from openapi_core import unmarshal_response
   from openapi_core.contrib.falcon import FalconOpenAPIResponse

   openapi_response = FalconOpenAPIResponse(falcon_response)
   result = unmarshal_response(openapi_request, openapi_response, spec=spec)


Flask
-----

This section describes integration with `Flask <https://flask.palletsprojects.com>`__ web framework.

Decorator
~~~~~~~~~

Flask views can be integrated by ``FlaskOpenAPIViewDecorator`` decorator.

.. code-block:: python

   from openapi_core.contrib.flask.decorators import FlaskOpenAPIViewDecorator

   openapi = FlaskOpenAPIViewDecorator.from_spec(spec)

   @app.route('/home')
   @openapi
   def home():
       pass

If you want to decorate class based view you can use the decorators attribute:

.. code-block:: python

   class MyView(View):
       decorators = [openapi]

View
~~~~

As an alternative to the decorator-based integration, a Flask method based views can be integrated by inheritance from ``FlaskOpenAPIView`` class.

.. code-block:: python

   from openapi_core.contrib.flask.views import FlaskOpenAPIView

   class MyView(FlaskOpenAPIView):
       pass

   app.add_url_rule('/home', view_func=MyView.as_view('home', spec))

Request parameters
~~~~~~~~~~~~~~~~~~

In Flask, all unmarshalled request data are provided as Flask request object's ``openapi.parameters`` attribute

.. code-block:: python

   from flask.globals import request

   @app.route('/browse/<id>/')
   @openapi
   def home():
       browse_id = request.openapi.parameters.path['id']
       page = request.openapi.parameters.query.get('page', 1)

Low level
~~~~~~~~~

You can use ``FlaskOpenAPIRequest`` as a Flask request factory:

.. code-block:: python

   from openapi_core import unmarshal_request
   from openapi_core.contrib.flask import FlaskOpenAPIRequest

   openapi_request = FlaskOpenAPIRequest(flask_request)
   result = unmarshal_request(openapi_request, spec=spec)

For response factory see `Werkzeug`_ integration.


Pyramid
-------

See `pyramid_openapi3 <https://github.com/niteoweb/pyramid_openapi3>`_ project.


Requests
--------

This section describes integration with `Requests <https://requests.readthedocs.io>`__ library.

Low level
~~~~~~~~~

You can use ``RequestsOpenAPIRequest`` as a Requests request factory:

.. code-block:: python

   from openapi_core import unmarshal_request
   from openapi_core.contrib.requests import RequestsOpenAPIRequest

   openapi_request = RequestsOpenAPIRequest(requests_request)
   result = unmarshal_request(openapi_request, spec=spec)

You can use ``RequestsOpenAPIResponse`` as a Requests response factory:

.. code-block:: python

   from openapi_core import unmarshal_response
   from openapi_core.contrib.requests import RequestsOpenAPIResponse

   openapi_response = RequestsOpenAPIResponse(requests_response)
   result = unmarshal_response(openapi_request, openapi_response, spec=spec)


You can use ``RequestsOpenAPIWebhookRequest`` as a Requests webhook request factory:

.. code-block:: python

   from openapi_core import unmarshal_request
   from openapi_core.contrib.requests import RequestsOpenAPIWebhookRequest

   openapi_webhook_request = RequestsOpenAPIWebhookRequest(requests_request, "my_webhook")
   result = unmarshal_request(openapi_webhook_request, spec=spec)


Starlette
---------

This section describes integration with `Starlette <https://www.starlette.io>`__  ASGI framework.

Low level
~~~~~~~~~

You can use ``StarletteOpenAPIRequest`` as a Starlette request factory:

.. code-block:: python

   from openapi_core import unmarshal_request
   from openapi_core.contrib.starlette import StarletteOpenAPIRequest

   openapi_request = StarletteOpenAPIRequest(starlette_request)
   result = unmarshal_request(openapi_request, spec=spec)

You can use ``StarletteOpenAPIResponse`` as a Starlette response factory:

.. code-block:: python

   from openapi_core import unmarshal_response
   from openapi_core.contrib.starlette import StarletteOpenAPIResponse

   openapi_response = StarletteOpenAPIResponse(starlette_response)
   result = unmarshal_response(openapi_request, openapi_response, spec=spec)


Tornado
-------

See `tornado-openapi3 <https://github.com/correl/tornado-openapi3>`_ project.


Werkzeug
--------

This section describes integration with `Werkzeug <https://werkzeug.palletsprojects.com>`__ a WSGI web application library.

Low level
~~~~~~~~~

You can use ``WerkzeugOpenAPIRequest`` as a Werkzeug request factory:

.. code-block:: python

   from openapi_core import unmarshal_request
   from openapi_core.contrib.werkzeug import WerkzeugOpenAPIRequest

   openapi_request = WerkzeugOpenAPIRequest(werkzeug_request)
   result = unmarshal_request(openapi_request, spec=spec)

You can use ``WerkzeugOpenAPIResponse`` as a Werkzeug response factory:

.. code-block:: python

   from openapi_core import unmarshal_response
   from openapi_core.contrib.werkzeug import WerkzeugOpenAPIResponse

   openapi_response = WerkzeugOpenAPIResponse(werkzeug_response)
   result = unmarshal_response(openapi_request, openapi_response, spec=spec)
