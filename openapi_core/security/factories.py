from typing import Dict, Type

from openapi_core.security.providers import (
    ApiKeyProvider, BaseProvider, HttpProvider, UnsupportedProvider,
)
from openapi_core.spec.paths import SpecPath


class SecurityProviderFactory:

    PROVIDERS: Dict[str, Type[BaseProvider]] = {
        'apiKey': ApiKeyProvider,
        'http': HttpProvider,
        'oauth2': UnsupportedProvider,
        'openIdConnect': UnsupportedProvider,
    }

    def create(self, scheme: SpecPath) -> BaseProvider:
        scheme_type = scheme['type']
        provider_class = self.PROVIDERS[scheme_type]
        return provider_class(scheme)
