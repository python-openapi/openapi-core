import pytest

from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.casting.schemas.factories import SchemaCastersFactory
from openapi_core.spec.paths import Spec


class TestSchemaCaster:
    @pytest.fixture
    def caster_factory(self):
        def create_caster(schema):
            return SchemaCastersFactory().create(schema)

        return create_caster

    def test_array_invalid_type(self, caster_factory):
        spec = {
            "type": "array",
            "items": {
                "type": "number",
            },
        }
        schema = Spec.from_dict(spec)
        value = ["test", "test2"]

        with pytest.raises(CastError):
            caster_factory(schema)(value)

    def test_array_invalid_value(self, caster_factory):
        spec = {
            "type": "array",
            "items": {
                "type": "number",
            },
        }
        schema = Spec.from_dict(spec)
        value = 3.14

        with pytest.raises(CastError):
            caster_factory(schema)(value)
