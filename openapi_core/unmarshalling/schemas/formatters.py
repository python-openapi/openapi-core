from typing import Callable, Optional, Type, Union


class Formatter:

    def validate(
        self,
        value: Optional[Union[int, float, bool, str, list, dict]],
    ) -> bool:
        return True

    def unmarshal(
        self,
        value: Optional[Union[int, float, bool, str, list, dict]],
    ):
        return value

    @classmethod
    def from_callables(
        cls,
        validate: Optional[
            Callable[
                [Optional[Union[int, float, bool, str, list, dict]]],
                bool
            ]
        ] = None,
        unmarshal: Optional[
            Callable[
                [Optional[Union[int, float, bool, str, list, dict]]],
                Union[int, float, bool, str, list, dict]
            ]
        ] = None,
    ) -> 'Formatter':
        attrs = {}
        if validate is not None:
            attrs['validate'] = staticmethod(validate)
        if unmarshal is not None:
            attrs['unmarshal'] = staticmethod(unmarshal)

        klass: Type['Formatter'] = type('Formatter', (cls, ), attrs)
        return klass()
