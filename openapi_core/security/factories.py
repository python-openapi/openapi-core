from openapi_core.security.providers import ApiKeyProvider
from openapi_core.security.providers import HttpProvider
from openapi_core.security.providers import UnsupportedProvider


class SecurityProviderFactory:

    PROVIDERS = {
        "apiKey": ApiKeyProvider,
        "http": HttpProvider,
        "oauth2": UnsupportedProvider,
        "openIdConnect": UnsupportedProvider,
    }

    def create(self, scheme):
        scheme_type = scheme["type"]
        provider_class = self.PROVIDERS[scheme_type]
        return provider_class(scheme)
