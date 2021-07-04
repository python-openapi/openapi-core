import pytest

from openapi_core.extensions.models.models import BaseModel
from openapi_core.extensions.models.models import Model


class TestBaseModelDict:
    def test_not_implemented(self):
        model = BaseModel()

        with pytest.raises(NotImplementedError):
            model.__dict__


class TestModelDict:
    def test_dict_empty(self):
        model = Model()

        result = model.__dict__

        assert result == {}

    def test_dict(self):
        properties = {
            "prop1": "value1",
            "prop2": "value2",
        }
        model = Model(properties)

        result = model.__dict__

        assert result == properties

    def test_attribute(self):
        prop_value = "value1"
        properties = {
            "prop1": prop_value,
        }
        model = Model(properties)

        result = model.prop1

        assert result == prop_value
