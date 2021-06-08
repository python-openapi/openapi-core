from pathlib import Path

from openapi_core import create_spec
from openapi_core.contrib.falcon.middlewares import FalconOpenAPIMiddleware
import yaml

openapi_spec_path = Path("tests/integration/data/v3.0/petstore.yaml")
spec_yaml = openapi_spec_path.read_text()
spec_dict = yaml.load(spec_yaml)
spec = create_spec(spec_dict)
openapi_middleware = FalconOpenAPIMiddleware.from_spec(spec)
