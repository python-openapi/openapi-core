import re
from functools import partial
from typing import Any
from typing import List
from typing import Mapping

from openapi_core.schema.protocols import SuportsGetAll
from openapi_core.schema.protocols import SuportsGetList


def split(value: str, separator: str = ",", step: int = 1) -> List[str]:
    parts = value.split(separator)

    if step == 1:
        return parts

    result = []
    for i in range(len(parts)):
        if i % step == 0:
            if i + 1 < len(parts):
                result.append(parts[i] + separator + parts[i + 1])
    return result


def delimited_loads(
    explode: bool,
    name: str,
    schema_type: str,
    location: Mapping[str, Any],
    delimiter: str,
) -> Any:
    value = location[name]

    explode_type = (explode, schema_type)
    if explode_type == (False, "array"):
        return split(value, separator=delimiter)
    if explode_type == (False, "object"):
        return dict(
            map(
                partial(split, separator=delimiter),
                split(value, separator=delimiter, step=2),
            )
        )

    raise ValueError("not available")


def matrix_loads(
    explode: bool, name: str, schema_type: str, location: Mapping[str, Any]
) -> Any:
    if explode == False:
        m = re.match(rf"^;{name}=(.*)$", location[f";{name}"])
        if m is None:
            raise KeyError(name)
        value = m.group(1)
        # ;color=blue,black,brown
        if schema_type == "array":
            return split(value)
        # ;color=R,100,G,200,B,150
        if schema_type == "object":
            return dict(map(split, split(value, step=2)))
        # .;color=blue
        return value
    else:
        # ;color=blue;color=black;color=brown
        if schema_type == "array":
            return re.findall(rf";{name}=([^;]*)", location[f";{name}*"])
        # ;R=100;G=200;B=150
        if schema_type == "object":
            value = location[f";{name}*"]
            return dict(
                map(
                    partial(split, separator="="),
                    split(value[1:], separator=";"),
                )
            )
        # ;color=blue
        m = re.match(rf"^;{name}=(.*)$", location[f";{name}*"])
        if m is None:
            raise KeyError(name)
        value = m.group(1)
        return value


def label_loads(
    explode: bool, name: str, schema_type: str, location: Mapping[str, Any]
) -> Any:
    if explode == False:
        value = location[f".{name}"]
        # .blue,black,brown
        if schema_type == "array":
            return split(value[1:])
        # .R,100,G,200,B,150
        if schema_type == "object":
            return dict(map(split, split(value[1:], separator=",", step=2)))
        # .blue
        return value[1:]
    else:
        value = location[f".{name}*"]
        # .blue.black.brown
        if schema_type == "array":
            return split(value[1:], separator=".")
        # .R=100.G=200.B=150
        if schema_type == "object":
            return dict(
                map(
                    partial(split, separator="="),
                    split(value[1:], separator="."),
                )
            )
        # .blue
        return value[1:]


def form_loads(
    explode: bool, name: str, schema_type: str, location: Mapping[str, Any]
) -> Any:
    explode_type = (explode, schema_type)
    # color=blue,black,brown
    if explode_type == (False, "array"):
        return split(location[name], separator=",")
    # color=blue&color=black&color=brown
    elif explode_type == (True, "array"):
        if name not in location:
            raise KeyError(name)
        if isinstance(location, SuportsGetAll):
            return location.getall(name)
        if isinstance(location, SuportsGetList):
            return location.getlist(name)
        return location[name]

    value = location[name]
    # color=R,100,G,200,B,150
    if explode_type == (False, "object"):
        return dict(map(split, split(value, separator=",", step=2)))
    # R=100&G=200&B=150
    elif explode_type == (True, "object"):
        return dict(
            map(partial(split, separator="="), split(value, separator="&"))
        )

    # color=blue
    return value


def simple_loads(
    explode: bool, name: str, schema_type: str, location: Mapping[str, Any]
) -> Any:
    value = location[name]

    # blue,black,brown
    if schema_type == "array":
        return split(value, separator=",")

    explode_type = (explode, schema_type)
    # R,100,G,200,B,150
    if explode_type == (False, "object"):
        return dict(map(split, split(value, separator=",", step=2)))
    # R=100,G=200,B=150
    elif explode_type == (True, "object"):
        return dict(
            map(partial(split, separator="="), split(value, separator=","))
        )

    # blue
    return value


def space_delimited_loads(
    explode: bool, name: str, schema_type: str, location: Mapping[str, Any]
) -> Any:
    return delimited_loads(
        explode, name, schema_type, location, delimiter="%20"
    )


def pipe_delimited_loads(
    explode: bool, name: str, schema_type: str, location: Mapping[str, Any]
) -> Any:
    return delimited_loads(explode, name, schema_type, location, delimiter="|")


def deep_object_loads(
    explode: bool, name: str, schema_type: str, location: Mapping[str, Any]
) -> Any:
    explode_type = (explode, schema_type)

    if explode_type != (True, "object"):
        raise ValueError("not available")

    keys_str = " ".join(location.keys())
    if not re.search(rf"{name}\[\w+\]", keys_str):
        raise KeyError(name)

    values = {}
    for key, value in location.items():
        # Split the key from the brackets.
        key_split = re.split(pattern=r"\[|\]", string=key)
        if key_split[0] == name:
            values[key_split[1]] = value
    return values
