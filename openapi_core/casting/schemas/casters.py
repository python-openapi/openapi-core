from openapi_core.casting.schemas.exceptions import CastError


class PrimitiveCaster:

    def __init__(self, schema, caster_callable):
        self.schema = schema
        self.caster_callable = caster_callable

    def __call__(self, value):
        if value is None:
            return value
        try:
            return self.caster_callable(value)
        except (ValueError, TypeError):
            raise CastError(value, self.schema['type'])


class DummyCaster:

    def __call__(self, value):
        return value


class ArrayCaster:

    def __init__(self, schema, casters_factory):
        self.schema = schema
        self.casters_factory = casters_factory

    @property
    def items_caster(self):
        return self.casters_factory.create(self.schema / 'items')

    def __call__(self, value):
        if value is None:
            return value
        return list(map(self.items_caster, value))
