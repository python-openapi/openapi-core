from pathlib import Path

from openapi_core import create_spec
from openapi_core.contrib.falcon.middlewares import FalconOpenAPIMiddleware
import yaml

openapi_spec_path = Path("tests/integration/data/v3.0/petstore.yaml")
spec_dict = yaml.load(openapi_spec_path.read_text(), yaml.Loader)
spec = create_spec(spec_dict)
openapi_middleware = FalconOpenAPIMiddleware.from_spec(spec)
