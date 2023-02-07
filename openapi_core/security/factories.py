from typing import Any
from typing import Dict
from typing import Type

from openapi_core.security.providers import ApiKeyProvider
from openapi_core.security.providers import BaseProvider
from openapi_core.security.providers import HttpProvider
from openapi_core.security.providers import UnsupportedProvider
from openapi_core.spec import Spec


class SecurityProviderFactory:
    PROVIDERS: Dict[str, Type[BaseProvider]] = {
        "apiKey": ApiKeyProvider,
        "http": HttpProvider,
        "oauth2": UnsupportedProvider,
        "openIdConnect": UnsupportedProvider,
    }

    def create(self, scheme: Spec) -> Any:
        scheme_type = scheme["type"]
        provider_class = self.PROVIDERS[scheme_type]
        return provider_class(scheme)
