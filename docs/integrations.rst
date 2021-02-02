Integrations
============

Bottle
------

See `bottle-openapi-3  <https://github.com/cope-systems/bottle-openapi-3>`_ project.


Django
------

This section describes integration with `Django <https://www.djangoproject.com>`__ web framework.

For Django 2.2 you can use DjangoOpenAPIRequest a Django request factory:

.. code-block:: python

   from openapi_core.validation.request.validators import RequestValidator
   from openapi_core.contrib.django import DjangoOpenAPIRequest

   openapi_request = DjangoOpenAPIRequest(django_request)
   validator = RequestValidator(spec)
   result = validator.validate(openapi_request)

You can use DjangoOpenAPIResponse as a Django response factory:

.. code-block:: python

   from openapi_core.validation.response.validators import ResponseValidator
   from openapi_core.contrib.django import DjangoOpenAPIResponse

   openapi_response = DjangoOpenAPIResponse(django_response)
   validator = ResponseValidator(spec)
   result = validator.validate(openapi_request, openapi_response)


Falcon
------

This section describes integration with `Falcon <https://falconframework.org>`__ web framework.

Middleware
~~~~~~~~~~

Falcon API can be integrated by `FalconOpenAPIMiddleware` middleware.

.. code-block:: python

   from openapi_core.contrib.falcon.middlewares import FalconOpenAPIMiddleware

   openapi_middleware = FalconOpenAPIMiddleware.from_spec(spec)
   api = falcon.API(middleware=[openapi_middleware])

Low level
~~~~~~~~~

For Falcon you can use FalconOpenAPIRequest a Falcon request factory:

.. code-block:: python

   from openapi_core.validation.request.validators import RequestValidator
   from openapi_core.contrib.falcon import FalconOpenAPIRequestFactory

   openapi_request = FalconOpenAPIRequestFactory.create(falcon_request)
   validator = RequestValidator(spec)
   result = validator.validate(openapi_request)

You can use FalconOpenAPIResponse as a Falcon response factory:

.. code-block:: python

   from openapi_core.validation.response.validators import ResponseValidator
   from openapi_core.contrib.falcon import FalconOpenAPIResponseFactory

   openapi_response = FalconOpenAPIResponseFactory.create(falcon_response)
   validator = ResponseValidator(spec)
   result = validator.validate(openapi_request, openapi_response)


Flask
-----

This section describes integration with `Flask <https://flask.palletsprojects.com>`__ web framework.

Decorator
~~~~~~~~~

Flask views can be integrated by `FlaskOpenAPIViewDecorator` decorator.

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

As an alternative to the decorator-based integration, Flask method based views can be integrated by inheritance from `FlaskOpenAPIView` class.

.. code-block:: python

   from openapi_core.contrib.flask.views import FlaskOpenAPIView

   class MyView(FlaskOpenAPIView):
       pass

   app.add_url_rule('/home', view_func=MyView.as_view('home', spec))

Request parameters
~~~~~~~~~~~~~~~~~~

In Flask, all unmarshalled request data are provided as Flask request object's openapi.parameters attribute

.. code-block:: python

   from flask.globals import request

   @app.route('/browse/<id>/')
   @openapi
   def home():
       browse_id = request.openapi.parameters.path['id']
       page = request.openapi.parameters.query.get('page', 1)

Low level
~~~~~~~~~

You can use FlaskOpenAPIRequest a Flask/Werkzeug request factory:

.. code-block:: python

   from openapi_core.validation.request.validators import RequestValidator
   from openapi_core.contrib.flask import FlaskOpenAPIRequest

   openapi_request = FlaskOpenAPIRequest(flask_request)
   validator = RequestValidator(spec)
   result = validator.validate(openapi_request)

You can use FlaskOpenAPIResponse as a Flask/Werkzeug response factory:

.. code-block:: python

   from openapi_core.validation.response.validators import ResponseValidator
   from openapi_core.contrib.flask import FlaskOpenAPIResponse

   openapi_response = FlaskOpenAPIResponse(flask_response)
   validator = ResponseValidator(spec)
   result = validator.validate(openapi_request, openapi_response)


Pyramid
-------

See `pyramid_openapi3  <https://github.com/niteoweb/pyramid_openapi3>`_ project.


Requests
--------

This section describes integration with `Requests <https://requests.readthedocs.io>`__ library.

Low level
~~~~~~~~~

For Requests you can use RequestsOpenAPIRequest a Requests request factory:

.. code-block:: python

   from openapi_core.validation.request.validators import RequestValidator
   from openapi_core.contrib.requests import RequestsOpenAPIRequest

   openapi_request = RequestsOpenAPIRequest(requests_request)
   validator = RequestValidator(spec)
   result = validator.validate(openapi_request)

You can use RequestsOpenAPIResponse as a Requests response factory:

.. code-block:: python

   from openapi_core.validation.response.validators import ResponseValidator
   from openapi_core.contrib.requests import RequestsOpenAPIResponse

   openapi_response = RequestsOpenAPIResponse(requests_response)
   validator = ResponseValidator(spec)
   result = validator.validate(openapi_request, openapi_response)
