from openapi_core.casting.schemas.exceptions import CastError


class BaseSchemaCaster:
    def __init__(self, schema):
        self.schema = schema

    def __call__(self, value):
        if value is None:
            return value

        return self.cast(value)

    def cast(self, value):
        raise NotImplementedError


class CallableSchemaCaster(BaseSchemaCaster):
    def __init__(self, schema, caster_callable):
        super().__init__(schema)
        self.caster_callable = caster_callable

    def cast(self, value):
        try:
            return self.caster_callable(value)
        except (ValueError, TypeError):
            raise CastError(value, self.schema["type"])


class DummyCaster(BaseSchemaCaster):
    def cast(self, value):
        return value


class ComplexCaster(BaseSchemaCaster):
    def __init__(self, schema, casters_factory):
        super().__init__(schema)
        self.casters_factory = casters_factory


class ArrayCaster(ComplexCaster):
    @property
    def items_caster(self):
        return self.casters_factory.create(self.schema / "items")

    def cast(self, value):
        try:
            return list(map(self.items_caster, value))
        except (ValueError, TypeError):
            raise CastError(value, self.schema["type"])
