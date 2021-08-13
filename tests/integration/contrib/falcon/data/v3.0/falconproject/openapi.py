from pathlib import Path

import yaml
from openapi_spec_validator import openapi_v30_spec_validator

from openapi_core import create_spec
from openapi_core.contrib.falcon.middlewares import FalconOpenAPIMiddleware

openapi_spec_path = Path("tests/integration/data/v3.0/petstore.yaml")
spec_dict = yaml.load(openapi_spec_path.read_text(), yaml.Loader)
spec = create_spec(spec_dict, spec_validator=openapi_v30_spec_validator)
openapi_middleware = FalconOpenAPIMiddleware.from_spec(spec)
