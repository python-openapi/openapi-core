"""OpenAPI core models module"""


class BaseModel(dict):
    """Base class for OpenAPI models."""

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


class ModelFactory(object):

    def create(self, properties, name=None):
        model = BaseModel
        if name is not None:
            model = type(name, (BaseModel, ), {})

        return model(**properties)
