import pytest

from openapi_core.util import forcebool


class TestForcebool:
    @pytest.mark.parametrize("val", ["y", "yes", "t", "true", "on", "1", True])
    def test_true(self, val):
        result = forcebool(val)
        assert result is True

    @pytest.mark.parametrize(
        "val", ["n", "no", "f", "false", "off", "0", False]
    )
    def test_false(self, val):
        result = forcebool(val)
        assert result is False

    @pytest.mark.parametrize("val", ["random", "idontknow", ""])
    def test_value_error(self, val):
        with pytest.raises(ValueError):
            forcebool(val)
