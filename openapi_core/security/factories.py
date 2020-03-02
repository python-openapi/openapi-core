from openapi_core.schema.security_schemes.enums import SecuritySchemeType
from openapi_core.security.providers import (
    ApiKeyProvider, HttpProvider, UnsupportedProvider,
)


class SecurityProviderFactory(object):

    PROVIDERS = {
        SecuritySchemeType.API_KEY: ApiKeyProvider,
        SecuritySchemeType.HTTP: HttpProvider,
    }

    def create(self, scheme):
        if scheme.type == SecuritySchemeType.API_KEY:
            return ApiKeyProvider(scheme)
        elif scheme.type == SecuritySchemeType.HTTP:
            return HttpProvider(scheme)
        return UnsupportedProvider(scheme)
