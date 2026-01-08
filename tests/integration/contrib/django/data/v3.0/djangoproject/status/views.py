from pathlib import Path
from typing import Any
from typing import Dict

from django.http import HttpResponse
from jsonschema_path import SchemaPath

from openapi_core.contrib.django.decorators import DjangoOpenAPIViewDecorator
from openapi_core.contrib.django.handlers import DjangoOpenAPIErrorsHandler


class AppDjangoOpenAPIValidRequestHandler(DjangoOpenAPIErrorsHandler):
    @classmethod
    def format_openapi_error(cls, error: BaseException) -> Dict[str, Any]:
        ret = DjangoOpenAPIErrorsHandler.format_openapi_error(error)
        ret["title"] = ret["title"].upper()
        return ret


check_minimal_spec = DjangoOpenAPIViewDecorator.from_spec(
    SchemaPath.from_file_path(
        Path("tests/integration/data/v3.0/minimal_with_servers.yaml")
    ),
    errors_handler_cls=AppDjangoOpenAPIValidRequestHandler,
)


@check_minimal_spec
def get_status(request):
    return HttpResponse("OK")
