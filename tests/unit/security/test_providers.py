import pytest

from openapi_core.schema.security_schemes.models import SecurityScheme
from openapi_core.security.providers import HttpProvider
from openapi_core.testing import MockRequest


class TestHttpProvider(object):

    @pytest.fixture
    def scheme(self):
        return SecurityScheme('http', scheme='bearer')

    @pytest.fixture
    def provider(self, scheme):
        return HttpProvider(scheme)

    def test_issue29427(self, provider):
        """Tests HttpProvider against Issue29427
        https://bugs.python.org/issue29427
        """
        jwt = 'MQ'
        headers = {
            'Authorization': 'Bearer {0}'.format(jwt),
        }
        request = MockRequest(
            'http://localhost', 'GET', '/pets',
            headers=headers,
        )

        result = provider(request)

        assert result == jwt
