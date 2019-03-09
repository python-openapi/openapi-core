from openapi_core.schema.schemas import exceptions
import pytest
import attr


def is_open_api_exception(exception_type):
    try:
        return issubclass(exception_type, exceptions.OpenAPISchemaError)
    except TypeError:
        return False


class TestExceptions:

    @pytest.mark.parametrize(
        "exception_type",
        (
            exception_type
            for exception_type_name in dir(exceptions)
            for exception_type in [getattr(exceptions, exception_type_name)]
            if is_open_api_exception(exception_type)
        )
    )
    def test_convert_to_string(self, exception_type):
        # verify that we can convert to a string without error
        args = ['x'] * len(attr.fields(exception_type))
        str(exception_type(*args))
