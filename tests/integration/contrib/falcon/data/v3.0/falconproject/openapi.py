from pathlib import Path

import yaml
from jsonschema_path import SchemaPath

from openapi_core.contrib.falcon.middlewares import FalconOpenAPIMiddleware

openapi_spec_path = Path("tests/integration/data/v3.0/petstore.yaml")
spec_dict = yaml.load(openapi_spec_path.read_text(), yaml.Loader)
spec = SchemaPath.from_dict(spec_dict)
openapi_middleware = FalconOpenAPIMiddleware.from_spec(
    spec,
    extra_media_type_deserializers={},
)
