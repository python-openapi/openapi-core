"""OpenAPI core templating paths datatypes module"""
from collections import namedtuple

Path = namedtuple("Path", ["path", "path_result"])
PathOperation = namedtuple(
    "PathOperation", ["path", "operation", "path_result"]
)
PathOperationServer = namedtuple(
    "PathOperationServer",
    ["path", "operation", "server", "path_result", "server_result"],
)
