import pytest

from openapi_core.security.providers import HttpProvider
from openapi_core.spec.paths import SpecPath
from openapi_core.testing import MockRequest


class TestHttpProvider(object):

    @pytest.fixture
    def spec(self):
        return {
            'type': 'http',
            'scheme': 'bearer',
        }

    @pytest.fixture
    def scheme(self, spec):
        return SpecPath.from_spec(spec)

    @pytest.fixture
    def provider(self, scheme):
        return HttpProvider(scheme)

    @pytest.mark.parametrize(
        'header',
        ['authorization', 'Authorization', 'AUTHORIZATION'],
    )
    def test_header(self, provider, header):
        """Tests HttpProvider against Issue29427
        https://bugs.python.org/issue29427
        """
        jwt = 'MQ'
        headers = {
            header: 'Bearer {0}'.format(jwt),
        }
        request = MockRequest(
            'http://localhost', 'GET', '/pets',
            headers=headers,
        )

        result = provider(request)

        assert result == jwt
