"""OpenAPI core templating paths datatypes module"""
from collections import namedtuple

Path = namedtuple("Path", ["path", "path_result"])
OperationPath = namedtuple(
    "OperationPath", ["path", "operation", "path_result"]
)
ServerOperationPath = namedtuple(
    "ServerOperationPath",
    ["path", "operation", "server", "path_result", "server_result"],
)
