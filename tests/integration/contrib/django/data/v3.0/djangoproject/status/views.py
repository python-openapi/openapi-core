from pathlib import Path

from django.http import HttpResponse
from jsonschema_path import SchemaPath

from openapi_core.contrib.django.decorators import DjangoOpenAPIViewDecorator

check_minimal_spec = DjangoOpenAPIViewDecorator.from_spec(
    SchemaPath.from_file_path(
        Path("tests/integration/data/v3.0/minimal_with_servers.yaml")
    )
)


@check_minimal_spec
def get_status(request):
    return HttpResponse("OK")
