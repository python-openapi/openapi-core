from openapi_core.spec.paths import SpecPath


def get_all_properties(schema: SpecPath) -> dict:
    properties = schema.get('properties', {})
    properties_dict = dict(list(properties.items()))

    if 'allOf'not in schema:
        return properties_dict

    for subschema in schema / 'allOf':
        subschema_props = get_all_properties(subschema)
        properties_dict.update(subschema_props)

    return properties_dict


def get_all_properties_names(schema: SpecPath) -> set:
    all_properties = get_all_properties(schema)
    return set(all_properties.keys())
