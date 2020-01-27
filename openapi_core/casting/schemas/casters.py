from openapi_core.schema.schemas.types import NoValue


class PrimitiveCaster(object):

    def __init__(self, caster_callable):
        self.caster_callable = caster_callable

    def __call__(self, value):
        if value in (None, NoValue):
            return value
        return self.caster_callable(value)


class DummyCaster(object):

    def __call__(self, value):
        return value


class ArrayCaster(object):

    def __init__(self, schema, casters_factory):
        self.schema = schema
        self.casters_factory = casters_factory

    @property
    def items_caster(self):
        return self.casters_factory.create(self.schema.items)

    def __call__(self, value):
        if value in (None, NoValue):
            return value
        return list(map(self.items_caster, value))
