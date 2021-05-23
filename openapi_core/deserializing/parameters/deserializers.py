from typing import Callable, List, Optional, Union
import warnings

from openapi_core.deserializing.parameters.exceptions import (
    EmptyQueryParameterValue, ParameterDeserializeError,
)
from openapi_core.schema.parameters import get_aslist, get_explode
from openapi_core.spec.paths import SpecPath


class BaseParameterDeserializer:

    def __init__(self, param_or_header: SpecPath, style: str):
        self.param_or_header = param_or_header
        self.style = style

    def __call__(
        self,
        value: Optional[Union[str, List[str]]],
    ) -> Optional[Union[str, List[str]]]:
        raise NotImplementedError


class UnsupportedStyleDeserializer(BaseParameterDeserializer):

    def __call__(
        self,
        value: Optional[Union[str, List[str]]],
    ) -> Optional[Union[str, List[str]]]:
        warnings.warn(f"Unsupported {self.style} style")
        return value


class CallableParameterDeserializer(BaseParameterDeserializer):

    def __init__(
        self,
        param_or_header: SpecPath,
        style: str,
        deserializer_callable: Callable[
            [Optional[Union[str, List[str]]]], Optional[Union[str, List[str]]]
        ],
    ):
        super().__init__(param_or_header, style)
        self.deserializer_callable = deserializer_callable

        self.aslist = get_aslist(self.param_or_header)
        self.explode = get_explode(self.param_or_header)

    def __call__(
        self,
        value: Optional[Union[str, List[str]]],
    ) -> Optional[Union[str, List[str]]]:
        if 'allowEmptyValue' in self.param_or_header:
            warnings.warn(
                "Use of allowEmptyValue property is deprecated",
                DeprecationWarning,
            )

        # if "in" not defined then it's a Header
        location_name = self.param_or_header.getkey('in', 'header')
        allow_empty_values = self.param_or_header.getkey(
            'allowEmptyValue', False)
        if (location_name == 'query' and value == "" and
                not allow_empty_values):
            name = self.param_or_header['name']
            raise EmptyQueryParameterValue(name)

        if not self.aslist or self.explode:
            return value
        try:
            return self.deserializer_callable(value)
        except (ValueError, TypeError, AttributeError):
            raise ParameterDeserializeError(
                location_name, self.style, str(value))
