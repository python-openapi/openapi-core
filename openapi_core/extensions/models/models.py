"""OpenAPI X-Model extension models module"""


class BaseModel(dict):
    """Base class for OpenAPI X-Model."""

    def __getattr__(self, attr_name):
        """Only search through properties if attribute not found normally.
        :type attr_name: str
        """
        try:
            return self[attr_name]
        except KeyError:
            raise AttributeError(
                'type object {0!r} has no attribute {1!r}'
                .format(type(self).__name__, attr_name)
            )
