"""OpenAPI core validation handlers module"""


class BaseOpenAPIErrorsHandler:

    @classmethod
    def handle(cls, errors):
        raise NotImplementedError
