from pathlib import Path

import yaml

from openapi_core import OpenAPISpec as Spec
from openapi_core.contrib.falcon.middlewares import FalconOpenAPIMiddleware

openapi_spec_path = Path("tests/integration/data/v3.0/petstore.yaml")
spec_dict = yaml.load(openapi_spec_path.read_text(), yaml.Loader)
spec = Spec.create(spec_dict)
openapi_middleware = FalconOpenAPIMiddleware.from_spec(spec)
