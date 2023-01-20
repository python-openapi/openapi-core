Usage
=====

Firstly create your specification object.

.. code-block:: python

   from openapi_core import Spec

   spec = Spec.from_file_path('openapi.json')

Now you can use it to validate against requests and/or responses. 

Request
-------

Use ``validate_request`` function to validate request against a given spec. By default, OpenAPI spec version is detected:

.. code-block:: python

   from openapi_core import validate_request

   # raise error if request is invalid
   result = validate_request(request, spec=spec)

Request object should implement OpenAPI Request protocol (See :doc:`integrations`).

(For OpenAPI v3.1) Use the same function to validate webhook request against a given spec.

.. code-block:: python

   # raise error if request is invalid
   result = validate_request(webhook_request, spec=spec)

Webhook request object should implement OpenAPI WebhookRequest protocol (See :doc:`integrations`).

Retrieve validated and unmarshalled request data from validation result

.. code-block:: python

   # get parameters object with path, query, cookies and headers parameters
   validated_params = result.parameters
   # or specific location parameters
   validated_path_params = result.parameters.path

   # get body
   validated_body = result.body

   # get security data
   validated_security = result.security

Response
--------

Use ``validate_response`` function to validate response against a given spec. By default, OpenAPI spec version is detected:

.. code-block:: python

   from openapi_core import validate_response

   # raise error if response is invalid
   result = validate_response(request, response, spec=spec)

Response object should implement OpenAPI Response protocol  (See :doc:`integrations`).

(For OpenAPI v3.1) Use the same function to validate response from webhook request against a given spec.

.. code-block:: python

   # raise error if request is invalid
   result = validate_response(webhook_request, response, spec=spec)

Retrieve validated and unmarshalled response data from validation result

.. code-block:: python

   # get headers
   validated_headers = result.headers

   # get data
   validated_data = result.data

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

   # get basic auth decoded credentials
   result.security['BasicAuth']

   # get api key
   result.security['ApiKeyAuth']

Supported security types:

* http – for Basic and Bearer HTTP authentications schemes
* apiKey – for API keys and cookie authentication

