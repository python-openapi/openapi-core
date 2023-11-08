import unittest

import pytest


@pytest.fixture(autouse=True)
def disable_builtin_socket(scope="session"):
    # ResourceWarning from pytest with responses 0.24.0 workaround
    # See https://github.com/getsentry/responses/issues/689
    with unittest.mock.patch("socket.socket"):
        yield
