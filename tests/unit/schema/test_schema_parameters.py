import pytest
from jsonschema_path import SchemaPath

from openapi_core.schema.parameters import get_explode
from openapi_core.schema.parameters import get_style


class TestGetStyle:
    @pytest.mark.parametrize(
        "location,expected",
        [
            ("query", "form"),
            ("path", "simple"),
            ("header", "simple"),
            ("cookie", "form"),
        ],
    )
    def test_defaults(self, location, expected):
        spec = {
            "name": "default",
            "in": location,
        }
        param = SchemaPath.from_dict(spec)
        result = get_style(param)

        assert result == expected

    @pytest.mark.parametrize(
        "style,location",
        [
            ("matrix", "path"),
            ("label", "apth"),
            ("form", "query"),
            ("form", "cookie"),
            ("simple", "path"),
            ("simple", "header"),
            ("spaceDelimited", "query"),
            ("pipeDelimited", "query"),
            ("deepObject", "query"),
        ],
    )
    def test_defined(self, style, location):
        spec = {
            "name": "default",
            "in": location,
            "style": style,
        }
        param = SchemaPath.from_dict(spec)
        result = get_style(param)

        assert result == style


class TestGetExplode:
    @pytest.mark.parametrize(
        "style,location",
        [
            ("matrix", "path"),
            ("label", "path"),
            ("simple", "path"),
            ("spaceDelimited", "query"),
            ("pipeDelimited", "query"),
            ("deepObject", "query"),
        ],
    )
    def test_defaults_false(self, style, location):
        spec = {
            "name": "default",
            "in": location,
            "style": style,
        }
        param = SchemaPath.from_dict(spec)
        result = get_explode(param)

        assert result is False

    @pytest.mark.parametrize("location", ["query", "cookie"])
    def test_defaults_true(self, location):
        spec = {
            "name": "default",
            "in": location,
            "style": "form",
        }
        param = SchemaPath.from_dict(spec)
        result = get_explode(param)

        assert result is True

    @pytest.mark.parametrize("location", ["path", "query", "cookie", "header"])
    @pytest.mark.parametrize(
        "style",
        [
            "matrix",
            "label",
            "form",
            "form",
            "simple",
            "spaceDelimited",
            "pipeDelimited",
            "deepObject",
        ],
    )
    @pytest.mark.parametrize(
        "schema_type",
        [
            "string",
            "array" "object",
        ],
    )
    @pytest.mark.parametrize("explode", [False, True])
    def test_defined(self, location, style, schema_type, explode):
        spec = {
            "name": "default",
            "in": location,
            "explode": explode,
            "schema": {
                "type": schema_type,
            },
        }
        param = SchemaPath.from_dict(spec)
        result = get_explode(param)

        assert result == explode
