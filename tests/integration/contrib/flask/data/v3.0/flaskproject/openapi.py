from pathlib import Path

import yaml
from jsonschema_path import SchemaPath

openapi_spec_path = Path("tests/integration/data/v3.0/petstore.yaml")
spec_dict = yaml.load(openapi_spec_path.read_text(), yaml.Loader)
spec = SchemaPath.from_dict(spec_dict)
