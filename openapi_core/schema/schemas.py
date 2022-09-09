from typing import Any
from typing import Dict
from typing import Set

from openapi_core.spec import Spec


def get_all_properties(schema: Spec) -> Dict[str, Any]:
    properties = schema.get("properties", {})
    properties_dict = dict(list(properties.items()))

    if "allOf" not in schema:
        return properties_dict

    for subschema in schema / "allOf":
        subschema_props = get_all_properties(subschema)
        properties_dict.update(subschema_props)

    return properties_dict


def get_all_properties_names(schema: Spec) -> Set[str]:
    all_properties = get_all_properties(schema)
    return set(all_properties.keys())
