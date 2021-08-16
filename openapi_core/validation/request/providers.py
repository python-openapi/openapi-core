"""OpenAPI core validation request providers module"""


class BaseRequestProvider:

    @classmethod
    def provide(cls, *args, **kwargs):
        raise NotImplementedError
