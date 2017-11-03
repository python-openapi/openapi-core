openapi-core
************

.. image:: https://img.shields.io/pypi/v/openapi-core.svg
     :target: https://pypi.python.org/pypi/openapi-core
.. image:: https://travis-ci.org/p1c2u/openapi-core.svg?branch=master
     :target: https://travis-ci.org/p1c2u/openapi-core
.. image:: https://img.shields.io/codecov/c/github/p1c2u/openapi-core/master.svg?style=flat
     :target: https://codecov.io/github/p1c2u/openapi-core?branch=master
.. image:: https://img.shields.io/pypi/pyversions/openapi-core.svg
     :target: https://pypi.python.org/pypi/openapi-core
.. image:: https://img.shields.io/pypi/format/openapi-core.svg
     :target: https://pypi.python.org/pypi/openapi-core
.. image:: https://img.shields.io/pypi/status/openapi-core.svg
     :target: https://pypi.python.org/pypi/openapi-core

About
=====

Openapi-core is a Python library that adds client-side and server-side support
for the `OpenAPI Specification v3.0.0 <https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md>`__.

Installation
============

Recommended way (via pip):

::

    $ pip install openapi-core

Alternatively you can download the code and install from the repository:

.. code-block:: bash

   $ pip install -e git+https://github.com/p1c2u/openapi-core.git#egg=openapi_core


Usage
=====

Firstly create your specification:

.. code-block:: python

   from openapi_core import create_spec

   spec = create_spec(spec_dict)

Now you can use it to validate requests

.. code-block:: python

   from openapi_core.validators import RequestValidator

   validator = RequestValidator(spec)
   result = validator.validate(request)

   # raise errors if request invalid
   result.raise_for_errors()

   # get list of errors
   errors = result.errors

and unmarshal request data from validation result

.. code-block:: python

   # get parameters dictionary with path, query, cookies and headers parameters
   validated_params = result.parameters

   # get body
   validated_body = result.body

or use shortcuts for simple validation

.. code-block:: python

   from openapi_core import validate_parameters, validate_body

   validated_params = validate_parameters(spec, request)
   validated_body = validate_body(spec, request)

Request object should implement BaseOpenAPIRequest interface. You can use FlaskOpenAPIRequest a Flask/Werkzeug request wrapper implementation:

.. code-block:: python

   from openapi_core.validators import RequestValidator
   from openapi_core.wrappers import FlaskOpenAPIRequest

   openapi_request = FlaskOpenAPIRequest(flask_request)
   validator = RequestValidator(spec)
   result = validator.validate(openapi_request)

Related projects
================
* `openapi-spec-validator <https://github.com/p1c2u/openapi-spec-validator>`__
