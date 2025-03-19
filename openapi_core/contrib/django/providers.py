"""OpenAPI core contrib django providers module"""

import warnings
from typing import cast

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from openapi_core import OpenAPI


def get_default_openapi_instance() -> OpenAPI:
    """
    Retrieves or initializes the OpenAPI instance based on Django settings
    (either OPENAPI or OPENAPI_SPEC).
    This function ensures the spec is only loaded once.
    """
    if hasattr(settings, "OPENAPI"):
        # Recommended (newer) approach
        return cast(OpenAPI, settings.OPENAPI)
    elif hasattr(settings, "OPENAPI_SPEC"):
        # Backward compatibility
        warnings.warn(
            "OPENAPI_SPEC is deprecated. Use OPENAPI in your settings instead.",
            DeprecationWarning,
        )
        return OpenAPI(settings.OPENAPI_SPEC)
    else:
        raise ImproperlyConfigured(
            "Neither OPENAPI nor OPENAPI_SPEC is defined in Django settings."
        )
