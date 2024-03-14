Amazon API Gateway
==================

This section describes integration with `Amazon API Gateway <https://aws.amazon.com/api-gateway/>`__.

It is useful for:

* `AWS Lambda integrations <https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html>`__ where Lambda functions handle events from API Gateway (Amazon API Gateway event format version 1.0 and 2.0).
* `AWS Lambda function URLs <https://docs.aws.amazon.com/lambda/latest/dg/lambda-urls.html>`__ where Lambda functions handle events from dedicated HTTP(S) endpoint (Amazon API Gateway event format version 2.0).

ANY method
----------

Amazon API Gateway defines special ``ANY`` method that catches all HTTP methods. It is specified as `x-amazon-apigateway-any-method <https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-swagger-extensions-any-method.html>`__ OpenAPI extension. The extension is handled within custom path finder and can be used by setting ``path_finder_cls`` to be ``APIGatewayPathFinder``:

.. code-block:: python
  :emphasize-lines: 1,4

    from openapi_core.contrib.aws import APIGatewayPathFinder

    config = Config(
        path_finder_cls=APIGatewayPathFinder,
    )
    openapi = OpenAPI.from_file_path('openapi.json', config=config)

Low level
---------

The integration defines classes useful for low level integration.

Request
^^^^^^^

Use ``APIGatewayEventV2OpenAPIRequest`` to create OpenAPI request from an API Gateway event (format version 2.0):

.. code-block:: python

    from openapi_core.contrib.aws import APIGatewayEventV2OpenAPIRequest

    def handler(event, context):
        openapi_request = APIGatewayEventV2OpenAPIRequest(event)
        result = openapi.unmarshal_request(openapi_request)
        return {
            "statusCode": 200,
            "body": "Hello world",
        }

If you use format version 1.0, then import and use ``APIGatewayEventOpenAPIRequest``.

Response
^^^^^^^^

Use ``APIGatewayEventV2ResponseOpenAPIResponse`` to create OpenAPI response from API Gateway event (format version 2.0) response:

.. code-block:: python

    from openapi_core.contrib.aws import APIGatewayEventV2ResponseOpenAPIResponse

    def handler(event, context):
        openapi_request = APIGatewayEventV2OpenAPIRequest(event)
        response = {
            "statusCode": 200,
            "body": "Hello world",
        }
        openapi_response = APIGatewayEventV2ResponseOpenAPIResponse(response)
        result = openapi.unmarshal_response(openapi_request, openapi_response)
        return response

If you use format version 1.0, then import and use ``APIGatewayEventResponseOpenAPIResponse``.
