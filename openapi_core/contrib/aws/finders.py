from openapi_core.templating.paths.finders import APICallPathFinder
from openapi_core.templating.paths.iterators import (
    CatchAllMethodOperationsIterator,
)


class APIGatewayPathFinder(APICallPathFinder):
    operations_iterator = CatchAllMethodOperationsIterator(
        "any",
        "x-amazon-apigateway-any-method",
    )


class APIGatewayIntegrationPathFinder(APICallPathFinder):
    operations_iterator = CatchAllMethodOperationsIterator(
        "any",
        "x-amazon-apigateway-any-method",
    )
