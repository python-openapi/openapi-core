"""OpenAPI core wrappers module"""
import warnings

from six.moves.urllib.parse import urljoin


class BaseOpenAPIRequest(object):

    host_url = NotImplemented
    path = NotImplemented
    path_pattern = NotImplemented
    method = NotImplemented

    parameters = NotImplemented
    body = NotImplemented

    mimetype = NotImplemented

    @property
    def full_url_pattern(self):
        return urljoin(self.host_url, self.path_pattern)

    def get_body(self, spec):
        warnings.warn(
            "`get_body` method is deprecated. "
            "Use RequestValidator instead.",
            DeprecationWarning,
        )
        # backward compatibility
        from openapi_core.shortcuts import validate_body
        return validate_body(spec, self, wrapper_class=None)

    def get_parameters(self, spec):
        warnings.warn(
            "`get_parameters` method is deprecated. "
            "Use RequestValidator instead.",
            DeprecationWarning,
        )
        # backward compatibility
        from openapi_core.shortcuts import validate_parameters
        return validate_parameters(spec, self, wrapper_class=None)


class BaseOpenAPIResponse(object):

    body = NotImplemented
    status_code = NotImplemented

    mimetype = NotImplemented
