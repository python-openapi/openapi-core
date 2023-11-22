Flask
======

This section describes integration with `Flask <https://flask.palletsprojects.com>`__ web framework.

Decorator
---------

Flask views can be integrated by ``FlaskOpenAPIViewDecorator`` decorator.

.. code-block:: python
  :emphasize-lines: 1,3,6

    from openapi_core.contrib.flask.decorators import FlaskOpenAPIViewDecorator

    openapi = FlaskOpenAPIViewDecorator.from_spec(spec)

    @app.route('/home')
    @openapi
    def home():
       return "Welcome home"

Additional customization parameters can be passed to the decorator.

.. code-block:: python
  :emphasize-lines: 5

    from openapi_core.contrib.flask.decorators import FlaskOpenAPIViewDecorator

    openapi = FlaskOpenAPIViewDecorator.from_spec(
       spec,
       extra_format_validators=extra_format_validators,
    )

You can skip response validation process: by setting ``response_cls`` to ``None``

.. code-block:: python
  :emphasize-lines: 5

    from openapi_core.contrib.flask.decorators import FlaskOpenAPIViewDecorator

    openapi = FlaskOpenAPIViewDecorator.from_spec(
       spec,
       response_cls=None,
    )

If you want to decorate class based view you can use the decorators attribute:

.. code-block:: python
  :emphasize-lines: 2

    class MyView(View):
       decorators = [openapi]

       def dispatch_request(self):
           return "Welcome home"

    app.add_url_rule('/home', view_func=MyView.as_view('home'))

View
----

As an alternative to the decorator-based integration, a Flask method based views can be integrated by inheritance from ``FlaskOpenAPIView`` class.

.. code-block:: python
  :emphasize-lines: 1,3,8

    from openapi_core.contrib.flask.views import FlaskOpenAPIView

    class MyView(FlaskOpenAPIView):
       def get(self):
           return "Welcome home"

    app.add_url_rule(
       '/home',
       view_func=MyView.as_view('home', spec),
    )

Additional customization parameters can be passed to the view.

.. code-block:: python
  :emphasize-lines: 10

    from openapi_core.contrib.flask.views import FlaskOpenAPIView

    class MyView(FlaskOpenAPIView):
       def get(self):
           return "Welcome home"

    app.add_url_rule(
       '/home',
       view_func=MyView.as_view(
           'home', spec,
           extra_format_validators=extra_format_validators,
       ),
    )

Request parameters
------------------

In Flask, all unmarshalled request data are provided as Flask request object's ``openapi.parameters`` attribute

.. code-block:: python
  :emphasize-lines: 6,7

    from flask.globals import request

    @app.route('/browse/<id>/')
    @openapi
    def browse(id):
       browse_id = request.openapi.parameters.path['id']
       page = request.openapi.parameters.query.get('page', 1)

       return f"Browse {browse_id}, page {page}"

Low level
---------

You can use ``FlaskOpenAPIRequest`` as a Flask request factory:

.. code-block:: python

    from openapi_core.contrib.flask import FlaskOpenAPIRequest

    openapi_request = FlaskOpenAPIRequest(flask_request)
    result = openapi.unmarshal_request(openapi_request)

For response factory see `Werkzeug <werkzeug.rst>`_ integration.
