import pytest
from jsonschema_path import SchemaPath
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.casting.schemas import oas31_schema_casters_factory
from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.deserializing.styles import style_deserializers
from openapi_core.deserializing.styles.factories import (
    StyleDeserializersFactory,
)
from openapi_core.schema.parameters import get_style_and_explode


class TestParameterStyleDeserializer:
    @pytest.fixture
    def spec(self):
        spec_dict = {}
        return SchemaPath.from_dict(spec_dict)

    @pytest.fixture
    def deserializer_factory(self, spec):
        style_deserializers_factory = StyleDeserializersFactory(
            oas31_schema_casters_factory,
            style_deserializers=style_deserializers,
        )

        def create_deserializer(param, name=None):
            name = name or param["name"]
            style, explode = get_style_and_explode(param)
            schema = param / "schema"
            return style_deserializers_factory.create(
                spec, schema, style, explode, name=name
            )

        return create_deserializer

    @pytest.mark.parametrize(
        "location_name", ["cookie", "header", "query", "path"]
    )
    @pytest.mark.parametrize("value", ["", "test"])
    def test_unsupported(self, deserializer_factory, location_name, value):
        name = "param"
        schema_type = "string"
        spec = {
            "name": name,
            "in": location_name,
            "style": "unsupported",
            "schema": {
                "type": schema_type,
            },
        }
        param = SchemaPath.from_dict(spec)
        deserializer = deserializer_factory(param)
        location = {name: value}

        with pytest.warns(UserWarning):
            result = deserializer.deserialize(location)

        assert result == value

    @pytest.mark.parametrize(
        "location_name,style,explode,schema_type,location",
        [
            ("query", "matrix", False, "string", {";param": "invalid"}),
            ("query", "matrix", False, "array", {";param": "invalid"}),
            ("query", "matrix", False, "object", {";param": "invalid"}),
            ("query", "matrix", True, "string", {";param*": "invalid"}),
            ("query", "deepObject", True, "object", {"param": "invalid"}),
            ("query", "form", True, "array", {}),
        ],
    )
    def test_name_not_found(
        self,
        deserializer_factory,
        location_name,
        style,
        explode,
        schema_type,
        location,
    ):
        name = "param"
        spec = {
            "name": name,
            "in": location_name,
            "style": style,
            "explode": explode,
            "schema": {
                "type": schema_type,
            },
        }
        param = SchemaPath.from_dict(spec)
        deserializer = deserializer_factory(param)

        with pytest.raises(KeyError):
            deserializer.deserialize(location)

    @pytest.mark.parametrize(
        "location_name,style,explode,schema_type,location",
        [
            ("path", "deepObject", False, "string", {"param": "invalid"}),
            ("path", "deepObject", False, "array", {"param": "invalid"}),
            ("path", "deepObject", False, "object", {"param": "invalid"}),
            ("path", "deepObject", True, "string", {"param": "invalid"}),
            ("path", "deepObject", True, "array", {"param": "invalid"}),
            ("path", "spaceDelimited", False, "string", {"param": "invalid"}),
            ("path", "pipeDelimited", False, "string", {"param": "invalid"}),
        ],
    )
    def test_combination_not_available(
        self,
        deserializer_factory,
        location_name,
        style,
        explode,
        schema_type,
        location,
    ):
        name = "param"
        spec = {
            "name": name,
            "in": location_name,
            "style": style,
            "explode": explode,
            "schema": {
                "type": schema_type,
            },
        }
        param = SchemaPath.from_dict(spec)
        deserializer = deserializer_factory(param)

        with pytest.raises(DeserializeError):
            deserializer.deserialize(location)

    @pytest.mark.parametrize(
        "explode,schema_type,location,expected",
        [
            (False, "string", {";param": ";param=blue"}, "blue"),
            (True, "string", {";param*": ";param=blue"}, "blue"),
            (
                False,
                "array",
                {";param": ";param=blue,black,brown"},
                ["blue", "black", "brown"],
            ),
            (
                True,
                "array",
                {";param*": ";param=blue;param=black;param=brown"},
                ["blue", "black", "brown"],
            ),
            (
                False,
                "object",
                {";param": ";param=R,100,G,200,B,150"},
                {
                    "R": "100",
                    "G": "200",
                    "B": "150",
                },
            ),
            (
                True,
                "object",
                {";param*": ";R=100;G=200;B=150"},
                {
                    "R": "100",
                    "G": "200",
                    "B": "150",
                },
            ),
        ],
    )
    def test_matrix_valid(
        self, deserializer_factory, explode, schema_type, location, expected
    ):
        name = "param"
        spec = {
            "name": name,
            "in": "path",
            "style": "matrix",
            "explode": explode,
            "schema": {
                "type": schema_type,
            },
        }
        param = SchemaPath.from_dict(spec)
        deserializer = deserializer_factory(param)

        result = deserializer.deserialize(location)

        assert result == expected

    @pytest.mark.parametrize(
        "explode,schema_type,location,expected",
        [
            (False, "string", {".param": ".blue"}, "blue"),
            (True, "string", {".param*": ".blue"}, "blue"),
            (
                False,
                "array",
                {".param": ".blue,black,brown"},
                ["blue", "black", "brown"],
            ),
            (
                True,
                "array",
                {".param*": ".blue.black.brown"},
                ["blue", "black", "brown"],
            ),
            (
                False,
                "object",
                {".param": ".R,100,G,200,B,150"},
                {
                    "R": "100",
                    "G": "200",
                    "B": "150",
                },
            ),
            (
                True,
                "object",
                {".param*": ".R=100.G=200.B=150"},
                {
                    "R": "100",
                    "G": "200",
                    "B": "150",
                },
            ),
        ],
    )
    def test_label_valid(
        self, deserializer_factory, explode, schema_type, location, expected
    ):
        name = "param"
        spec = {
            "name": name,
            "in": "path",
            "style": "label",
            "explode": explode,
            "schema": {
                "type": schema_type,
            },
        }
        param = SchemaPath.from_dict(spec)
        deserializer = deserializer_factory(param)

        result = deserializer.deserialize(location)

        assert result == expected

    @pytest.mark.parametrize("location_name", ["query", "cookie"])
    @pytest.mark.parametrize(
        "explode,schema_type,location,expected",
        [
            (False, "string", {"param": "blue"}, "blue"),
            (True, "string", {"param": "blue"}, "blue"),
            (
                False,
                "array",
                {"param": "blue,black,brown"},
                ["blue", "black", "brown"],
            ),
            (
                True,
                "array",
                ImmutableMultiDict(
                    [("param", "blue"), ("param", "black"), ("param", "brown")]
                ),
                ["blue", "black", "brown"],
            ),
            (
                False,
                "object",
                {"param": "R,100,G,200,B,150"},
                {
                    "R": "100",
                    "G": "200",
                    "B": "150",
                },
            ),
            (
                True,
                "object",
                {"param": "R=100&G=200&B=150"},
                {
                    "R": "100",
                    "G": "200",
                    "B": "150",
                },
            ),
        ],
    )
    def test_form_valid(
        self,
        deserializer_factory,
        location_name,
        explode,
        schema_type,
        location,
        expected,
    ):
        name = "param"
        spec = {
            "name": name,
            "in": location_name,
            "explode": explode,
            "schema": {
                "type": schema_type,
            },
        }
        param = SchemaPath.from_dict(spec)
        deserializer = deserializer_factory(param)

        result = deserializer.deserialize(location)

        assert result == expected

    @pytest.mark.parametrize("location_name", ["path", "header"])
    @pytest.mark.parametrize(
        "explode,schema_type,value,expected",
        [
            (False, "string", "blue", "blue"),
            (True, "string", "blue", "blue"),
            (False, "array", "blue,black,brown", ["blue", "black", "brown"]),
            (True, "array", "blue,black,brown", ["blue", "black", "brown"]),
            (
                False,
                "object",
                "R,100,G,200,B,150",
                {
                    "R": "100",
                    "G": "200",
                    "B": "150",
                },
            ),
            (
                True,
                "object",
                "R=100,G=200,B=150",
                {
                    "R": "100",
                    "G": "200",
                    "B": "150",
                },
            ),
        ],
    )
    def test_simple_valid(
        self,
        deserializer_factory,
        location_name,
        explode,
        schema_type,
        value,
        expected,
    ):
        name = "param"
        spec = {
            "name": name,
            "in": location_name,
            "explode": explode,
            "schema": {
                "type": schema_type,
            },
        }
        param = SchemaPath.from_dict(spec)
        deserializer = deserializer_factory(param)
        location = {name: value}

        result = deserializer.deserialize(location)

        assert result == expected

    @pytest.mark.parametrize(
        "schema_type,value,expected",
        [
            ("array", "blue%20black%20brown", ["blue", "black", "brown"]),
            (
                "object",
                "R%20100%20G%20200%20B%20150",
                {
                    "R": "100",
                    "G": "200",
                    "B": "150",
                },
            ),
        ],
    )
    def test_space_delimited_valid(
        self, deserializer_factory, schema_type, value, expected
    ):
        name = "param"
        spec = {
            "name": name,
            "in": "query",
            "style": "spaceDelimited",
            "explode": False,
            "schema": {
                "type": schema_type,
            },
        }
        param = SchemaPath.from_dict(spec)
        deserializer = deserializer_factory(param)
        location = {name: value}

        result = deserializer.deserialize(location)

        assert result == expected

    @pytest.mark.parametrize(
        "schema_type,value,expected",
        [
            ("array", "blue|black|brown", ["blue", "black", "brown"]),
            (
                "object",
                "R|100|G|200|B|150",
                {
                    "R": "100",
                    "G": "200",
                    "B": "150",
                },
            ),
        ],
    )
    def test_pipe_delimited_valid(
        self, deserializer_factory, schema_type, value, expected
    ):
        name = "param"
        spec = {
            "name": name,
            "in": "query",
            "style": "pipeDelimited",
            "explode": False,
            "schema": {
                "type": schema_type,
            },
        }
        param = SchemaPath.from_dict(spec)
        deserializer = deserializer_factory(param)
        location = {name: value}

        result = deserializer.deserialize(location)

        assert result == expected

    @pytest.mark.parametrize(
        "schema_types,value,expected",
        [
            # ``string`` is first → identity wins.
            (["string", "number", "boolean"], "12567", "12567"),
            # ``integer`` is first → coerced to int.
            (["integer", "string"], "42", 42),
        ],
    )
    def test_oas31_multi_type_form(
        self, deserializer_factory, schema_types, value, expected
    ):
        """Test OAS 3.1 multi-type support for form style parameters."""
        name = "param"
        spec = {
            "name": name,
            "in": "query",
            "explode": True,
            "schema": {
                "type": schema_types,
            },
        }
        param = SchemaPath.from_dict(spec)
        deserializer = deserializer_factory(param)
        location = {name: value}

        result = deserializer.deserialize(location)

        assert result == expected

    def test_deep_object_valid(self, deserializer_factory):
        name = "param"
        spec = {
            "name": name,
            "in": "query",
            "style": "deepObject",
            "explode": True,
            "schema": {
                "type": "object",
            },
        }
        param = SchemaPath.from_dict(spec)
        deserializer = deserializer_factory(param)
        location = {
            "param[R]": "100",
            "param[G]": "200",
            "param[B]": "150",
            "other[0]": "value",
        }

        result = deserializer.deserialize(location)

        assert result == {
            "R": "100",
            "G": "200",
            "B": "150",
        }

    def test_simple_array_or_null(self, deserializer_factory):
        """OAS 3.1 ``type: ["array", "null"]`` is parsed as an array."""
        name = "param"
        spec = {
            "name": name,
            "in": "path",
            "style": "simple",
            "schema": {
                "type": ["array", "null"],
                "items": {"type": "integer"},
            },
        }
        param = SchemaPath.from_dict(spec)
        deserializer = deserializer_factory(param)
        location = {name: "1,2,3"}

        result = deserializer.deserialize(location)

        assert result == [1, 2, 3]

    def test_form_array_or_null_explode(self, deserializer_factory):
        """OAS 3.1 ``type: ["array", "null"]`` with form/explode fans out."""
        name = "param"
        spec = {
            "name": name,
            "in": "query",
            "style": "form",
            "explode": True,
            "schema": {
                "type": ["array", "null"],
                "items": {"type": "integer"},
            },
        }
        param = SchemaPath.from_dict(spec)
        deserializer = deserializer_factory(param)
        location = ImmutableMultiDict([(name, "1"), (name, "2"), (name, "3")])

        result = deserializer.deserialize(location)

        assert result == [1, 2, 3]

    def test_form_object_or_null(self, deserializer_factory):
        """OAS 3.1 ``type: ["object", "null"]`` is parsed as an object."""
        name = "param"
        spec = {
            "name": name,
            "in": "query",
            "style": "form",
            "explode": False,
            "schema": {
                "type": ["object", "null"],
                "properties": {
                    "R": {"type": "integer"},
                    "G": {"type": "integer"},
                    "B": {"type": "integer"},
                },
            },
        }
        param = SchemaPath.from_dict(spec)
        deserializer = deserializer_factory(param)
        location = {name: "R,100,G,200,B,150"}

        result = deserializer.deserialize(location)

        assert result == {"R": 100, "G": 200, "B": 150}

    def test_simple_primitive_or_null(self, deserializer_factory):
        """OAS 3.1 ``type: ["integer", "null"]`` simple style coerces."""
        name = "param"
        spec = {
            "name": name,
            "in": "path",
            "style": "simple",
            "schema": {"type": ["integer", "null"]},
        }
        param = SchemaPath.from_dict(spec)
        deserializer = deserializer_factory(param)
        location = {name: "42"}

        result = deserializer.deserialize(location)

        assert result == 42
        assert type(result) is int
