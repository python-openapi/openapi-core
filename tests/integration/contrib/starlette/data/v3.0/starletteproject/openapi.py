from pathlib import Path

import yaml

from openapi_core import OpenAPI

openapi_spec_path = Path("tests/integration/data/v3.0/petstore.yaml")
spec_dict = yaml.load(openapi_spec_path.read_text(), yaml.Loader)
openapi = OpenAPI.from_dict(spec_dict)
