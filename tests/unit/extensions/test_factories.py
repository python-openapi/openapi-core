from dataclasses import dataclass
from dataclasses import is_dataclass
from sys import modules
from types import ModuleType
from typing import Any

import pytest
from jsonschema_path import SchemaPath

from openapi_core.extensions.models.factories import ModelPathFactory


class TestImportModelCreate:
    @pytest.fixture
    def loaded_model_class(self):
        @dataclass
        class BarModel:
            a: str
            b: int

        foo_module = ModuleType("foo")
        foo_module.BarModel = BarModel
        modules["foo"] = foo_module
        yield BarModel
        del modules["foo"]

    def test_dynamic_model(self):
        factory = ModelPathFactory()

        schema = SchemaPath.from_dict({"x-model": "TestModel"})
        test_model_class = factory.create(schema, ["name"])

        assert is_dataclass(test_model_class)
        assert test_model_class.__name__ == "TestModel"
        assert list(test_model_class.__dataclass_fields__.keys()) == ["name"]
        assert str(test_model_class.__dataclass_fields__["name"].type) == str(
            Any
        )

    def test_model_path(self, loaded_model_class):
        factory = ModelPathFactory()

        schema = SchemaPath.from_dict({"x-model-path": "foo.BarModel"})
        test_model_class = factory.create(schema, ["a", "b"])

        assert test_model_class == loaded_model_class
