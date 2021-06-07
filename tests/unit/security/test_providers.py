import pytest

from openapi_core.security.providers import HttpProvider
from openapi_core.spec.paths import SpecPath
from openapi_core.testing import MockRequest


class TestHttpProvider:

    @pytest.mark.parametrize(
        'header',
        ['authorization', 'Authorization', 'AUTHORIZATION'],
    )
    @pytest.mark.parametrize(
        'scheme',
        ['basic', 'bearer', 'digest'],
    )
    def test_header(self, header, scheme):
        """Tests HttpProvider against Issue29427
        https://bugs.python.org/issue29427
        """
        spec = {
            'type': 'http',
            'scheme': scheme,
        }
        value = 'MQ'
        headers = {
            header: ' '.join([scheme.title(), value]),
        }
        request = MockRequest(
            'http://localhost', 'GET', '/pets',
            headers=headers,
        )
        scheme = SpecPath.from_spec(spec)
        provider = HttpProvider(scheme)

        result = provider(request)

        assert result == value
