from typing import Any
from typing import Dict
from typing import Optional
from typing import Type

import pytest
from jsonschema_path import SchemaPath

from openapi_core import V31RequestValidator
from openapi_core import V32RequestValidator
from openapi_core.testing import MockRequest
from openapi_core.validation.request.exceptions import InvalidRequestBody


def _spec_dict(
    openapi_version: str,
    dialect: Optional[str] = None,
    schema_dialect: Optional[str] = None,
) -> Dict[str, Any]:
    schema = {"type": "integer", "minimum": 10, "exclusiveMinimum": True}
    if schema_dialect is not None:
        schema["$schema"] = schema_dialect

    spec = {
        "openapi": openapi_version,
        "info": {"title": "Dialect Validation", "version": "1.0.0"},
        "servers": [{"url": "http://example.com"}],
        "paths": {
            "/users": {
                "post": {
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": schema}},
                    },
                    "responses": {"200": {"description": "OK"}},
                }
            }
        },
    }
    if dialect is not None:
        spec["jsonSchemaDialect"] = dialect

    return spec


@pytest.mark.parametrize(
    "openapi_version, validator_cls",
    [
        ("3.1.0", V31RequestValidator),
        ("3.2.0", V32RequestValidator),
    ],
)
class TestDialectValidators:
    def test_default_dialect_valid(
        self, openapi_version: str, validator_cls: Type[Any]
    ) -> None:
        spec = _spec_dict(openapi_version=openapi_version)
        spec_path = SchemaPath.from_dict(spec)
        validator = validator_cls(spec_path)

        request = MockRequest(
            "http://example.com",
            "POST",
            "/users",
            data=b"10",
            content_type="application/json",
        )
        validator.validate(request)

    def test_unsupported_json_schema_dialect(
        self, openapi_version: str, validator_cls: Type[Any]
    ) -> None:
        spec = _spec_dict(
            openapi_version=openapi_version,
            dialect="http://unsupported.dialect",
        )
        spec_path = SchemaPath.from_dict(spec)

        validator = validator_cls(spec_path)
        request = MockRequest(
            "http://example.com",
            "POST",
            "/users",
            data=b"10",
            content_type="application/json",
        )
        with pytest.raises(
            ValueError,
            match="Unknown JSON Schema dialect: 'http://unsupported.dialect'",
        ):
            validator.validate(request)

    def test_unsupported_schema_dialect(
        self, openapi_version: str, validator_cls: Type[Any]
    ) -> None:
        spec = _spec_dict(
            openapi_version=openapi_version,
            schema_dialect="http://unsupported.dialect",
        )
        spec_path = SchemaPath.from_dict(spec)

        validator = validator_cls(spec_path)
        request = MockRequest(
            "http://example.com",
            "POST",
            "/users",
            data=b"10",
            content_type="application/json",
        )
        with pytest.raises(
            ValueError,
            match="Unknown JSON Schema dialect: 'http://unsupported.dialect'",
        ):
            validator.validate(request)

    def test_valid_json_schema_dialect(
        self, openapi_version: str, validator_cls: Type[Any]
    ) -> None:
        # Using draft-04 dialect
        spec = _spec_dict(
            openapi_version=openapi_version,
            dialect="http://json-schema.org/draft-04/schema#",
        )
        spec_path = SchemaPath.from_dict(spec)

        validator = validator_cls(spec_path)
        request = MockRequest(
            "http://example.com",
            "POST",
            "/users",
            data=b"15",
            content_type="application/json",
        )
        validator.validate(request)

    def test_valid_json_schema_dialect_invalid_data(
        self, openapi_version: str, validator_cls: Type[Any]
    ) -> None:
        # Using draft-04 dialect, where `exclusiveMinimum: true` makes 10 invalid
        spec = _spec_dict(
            openapi_version=openapi_version,
            dialect="http://json-schema.org/draft-04/schema#",
        )
        spec_path = SchemaPath.from_dict(spec)

        validator = validator_cls(spec_path)
        request = MockRequest(
            "http://example.com",
            "POST",
            "/users",
            data=b"10",
            content_type="application/json",
        )
        with pytest.raises(InvalidRequestBody):
            validator.validate(request)
