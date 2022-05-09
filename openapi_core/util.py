"""OpenAPI core util module"""


def forcebool(val):
    if isinstance(val, str):
        val = val.lower()
        if val in ("y", "yes", "t", "true", "on", "1"):
            return True
        elif val in ("n", "no", "f", "false", "off", "0"):
            return False
        else:
            raise ValueError(f"invalid truth value {val!r}")

    return bool(val)
