Usage
=====

Firstly create your specification:

.. code-block:: python

   from openapi_core import create_spec

   spec = create_spec(spec_dict)


Request
-------

Now you can use it to validate requests

.. code-block:: python

   from openapi_core.validation.request.validators import RequestValidator

   validator = RequestValidator(spec)
   result = validator.validate(request)

   # raise errors if request invalid
   result.raise_for_errors()

   # get list of errors
   errors = result.errors

and unmarshal request data from validation result

.. code-block:: python

   # get parameters object with path, query, cookies and headers parameters
   validated_params = result.parameters
   # or specific parameters
   validated_path_params = result.parameters.path

   # get body
   validated_body = result.body

   # get security data
   validated_security = result.security

Request object should be instance of OpenAPIRequest class (See :doc:`integrations`).

Response
--------

You can also validate responses

.. code-block:: python

   from openapi_core.validation.response.validators import ResponseValidator

   validator = ResponseValidator(spec)
   result = validator.validate(request, response)

   # raise errors if response invalid
   result.raise_for_errors()

   # get list of errors
   errors = result.errors

and unmarshal response data from validation result

.. code-block:: python

   # get headers
   validated_headers = result.headers

   # get data
   validated_data = result.data

Response object should be instance of OpenAPIResponse class (See :doc:`integrations`).

Security
--------

openapi-core supports security for authentication and authorization process. Security data for security schemas are accessible from `security` attribute of `RequestValidationResult` object.

For given security specification:

.. code-block:: yaml

   security:
     - BasicAuth: []
     - ApiKeyAuth: []
   components:
     securitySchemes:
       BasicAuth:
         type: http
         scheme: basic
       ApiKeyAuth:
         type: apiKey
         in: header
         name: X-API-Key

you can access your security data the following:

.. code-block:: python

   result = validator.validate(request)

   # get basic auth decoded credentials
   result.security['BasicAuth']

   # get api key
   result.security['ApiKeyAuth']

Supported security types:

* http – for Basic and Bearer HTTP authentications schemes
* apiKey – for API keys and cookie authentication

