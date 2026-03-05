from typing import cast
from unittest.mock import patch

from jsonschema._format import FormatChecker
from jsonschema.protocols import Validator

from openapi_core.validation.schemas.factories import (
    DialectSchemaValidatorsFactory,
)


class MockValidator:
    FORMAT_CHECKER = FormatChecker()


class TestDialectSchemaValidatorsFactoryCaching:
    def test_get_validator_class_for_dialect_is_cached(self):
        factory = DialectSchemaValidatorsFactory(
            schema_validator_cls=cast(type[Validator], MockValidator),
            default_jsonschema_dialect_id="http://json-schema.org/draft-04/schema#",
            format_checker=FormatChecker(),
        )

        with patch(
            "openapi_core.validation.schemas.factories.validator_for"
        ) as mock_validator_for:
            mock_validator_for.return_value = "MockedClass"

            # Call first time
            result1 = factory._get_validator_class_for_dialect(
                "http://json-schema.org/draft-04/schema#"
            )

            # Call second time with same dialect
            result2 = factory._get_validator_class_for_dialect(
                "http://json-schema.org/draft-04/schema#"
            )

            # Assert results are same
            assert result1 == "MockedClass"
            assert result2 == "MockedClass"

            # Assert `validator_for` was only called once because of cache
            mock_validator_for.assert_called_once_with(
                {"$schema": "http://json-schema.org/draft-04/schema#"},
                default=None,
            )

        # Let's also check with another dialect
        with patch(
            "openapi_core.validation.schemas.factories.validator_for"
        ) as mock_validator_for2:
            mock_validator_for2.return_value = "MockedClass2"

            result3 = factory._get_validator_class_for_dialect(
                "https://json-schema.org/draft/2020-12/schema"
            )
            assert result3 == "MockedClass2"
            mock_validator_for2.assert_called_once()
