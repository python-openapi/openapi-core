Usage
=====

Firstly create your specification object. By default, OpenAPI spec version is detected:

.. code-block:: python

   from openapi_core import Spec

   spec = Spec.from_file_path('openapi.json')


Request
-------

Now you can use it to validate against requests

.. code-block:: python

   from openapi_core import validate_request

   # raise error if request is invalid
   result = validate_request(request, spec=spec)

and unmarshal request data from validation result

.. code-block:: python

   # get parameters object with path, query, cookies and headers parameters
   validated_params = result.parameters
   # or specific location parameters
   validated_path_params = result.parameters.path

   # get body
   validated_body = result.body

   # get security data
   validated_security = result.security

Request object should implement OpenAPI Request protocol (See :doc:`integrations`).

Response
--------

You can also validate against responses

.. code-block:: python

   from openapi_core import validate_response

   # raise error if response is invalid
   result = validate_response(request, response, spec=spec)

and unmarshal response data from validation result

.. code-block:: python

   # get headers
   validated_headers = result.headers

   # get data
   validated_data = result.data

Response object should implement OpenAPI Response protocol  (See :doc:`integrations`).

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

