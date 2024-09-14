# Flask

This section describes integration with [Flask](https://flask.palletsprojects.com) web framework.

## View decorator

Flask can be integrated by [view decorator](https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/) to apply OpenAPI validation to your application's specific views.

Use `FlaskOpenAPIViewDecorator` with OpenAPI object to create the decorator.

``` python hl_lines="1 3 6"
from openapi_core.contrib.flask.decorators import FlaskOpenAPIViewDecorator

openapi_validated = FlaskOpenAPIViewDecorator(openapi)

@app.route('/home')
@openapi_validated
def home():
    return "Welcome home"
```

You can skip response validation process: by setting `response_cls` to `None`

``` python hl_lines="5"
from openapi_core.contrib.flask.decorators import FlaskOpenAPIViewDecorator

openapi_validated = FlaskOpenAPIViewDecorator(
    openapi,
    response_cls=None,
)
```

If you want to decorate class based view you can use the decorators attribute:

``` python hl_lines="2"
class MyView(View):
    decorators = [openapi_validated]

    def dispatch_request(self):
        return "Welcome home"

app.add_url_rule('/home', view_func=MyView.as_view('home'))
```

## View

As an alternative to the decorator-based integration, a Flask method based views can be integrated by inheritance from `FlaskOpenAPIView` class.

``` python hl_lines="1 3 8"
from openapi_core.contrib.flask.views import FlaskOpenAPIView

class MyView(FlaskOpenAPIView):
    def get(self):
        return "Welcome home"

app.add_url_rule(
    '/home',
    view_func=MyView.as_view('home', spec),
)
```

Additional customization parameters can be passed to the view.

``` python hl_lines="10"
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
```

## Request parameters

In Flask, all unmarshalled request data are provided as Flask request object's `openapi.parameters` attribute

``` python hl_lines="6 7"
from flask.globals import request

@app.route('/browse/<id>/')
@openapi
def browse(id):
    browse_id = request.openapi.parameters.path['id']
    page = request.openapi.parameters.query.get('page', 1)

    return f"Browse {browse_id}, page {page}"
```

## Low level

You can use `FlaskOpenAPIRequest` as a Flask request factory:

```python
from openapi_core.contrib.flask import FlaskOpenAPIRequest

openapi_request = FlaskOpenAPIRequest(flask_request)
result = openapi.unmarshal_request(openapi_request)
```

For response factory see [Werkzeug](werkzeug.md) integration.
