from typing import Any
from typing import Dict

from openapi_core.spec import Spec


def get_properties(schema: Spec) -> Dict[str, Any]:
    properties = schema.get("properties", {})
    properties_dict = dict(list(properties.items()))
    return properties_dict
