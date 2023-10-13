from typing import Any
from typing import Dict

from jsonschema_path import SchemaPath


def get_properties(schema: SchemaPath) -> Dict[str, Any]:
    properties = schema.get("properties", {})
    properties_dict = dict(list(properties.items()))
    return properties_dict
