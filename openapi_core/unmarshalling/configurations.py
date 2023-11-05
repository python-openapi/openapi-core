from dataclasses import dataclass
from typing import Optional

from openapi_core.unmarshalling.schemas.datatypes import (
    FormatUnmarshallersDict,
)
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)
from openapi_core.validation.configurations import ValidatorConfig


@dataclass
class UnmarshallerConfig(ValidatorConfig):
    """Unmarshaller configuration dataclass.

    Attributes:
        schema_unmarshallers_factory
            Schema unmarshallers factory.
        extra_format_unmarshallers
            Extra format unmarshallers.
    """

    schema_unmarshallers_factory: Optional[SchemaUnmarshallersFactory] = None
    extra_format_unmarshallers: Optional[FormatUnmarshallersDict] = None
