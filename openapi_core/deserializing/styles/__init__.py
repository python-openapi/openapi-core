from openapi_core.deserializing.styles.datatypes import StyleDeserializersDict
from openapi_core.deserializing.styles.factories import (
    StyleDeserializersFactory,
)
from openapi_core.deserializing.styles.util import deep_object_loads
from openapi_core.deserializing.styles.util import form_loads
from openapi_core.deserializing.styles.util import label_loads
from openapi_core.deserializing.styles.util import matrix_loads
from openapi_core.deserializing.styles.util import pipe_delimited_loads
from openapi_core.deserializing.styles.util import simple_loads
from openapi_core.deserializing.styles.util import space_delimited_loads

__all__ = ["style_deserializers_factory"]

style_deserializers: StyleDeserializersDict = {
    "matrix": matrix_loads,
    "label": label_loads,
    "form": form_loads,
    "simple": simple_loads,
    "spaceDelimited": space_delimited_loads,
    "pipeDelimited": pipe_delimited_loads,
    "deepObject": deep_object_loads,
}

style_deserializers_factory = StyleDeserializersFactory(
    style_deserializers=style_deserializers,
)
