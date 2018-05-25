"""OpenAPI core parameters enums module"""
from enum import Enum


class ParameterLocation(Enum):

    PATH = 'path'
    QUERY = 'query'
    HEADER = 'header'
    COOKIE = 'cookie'

    @classmethod
    def has_value(cls, value):
        return (any(value == item.value for item in cls))


class ParameterStyle(Enum):

    MATRIX = 'matrix'
    LABEL = 'label'
    FORM = 'form'
    SIMPLE = 'simple'
    SPACE_DELIMITED = 'spaceDelimited'
    PIPE_DELIMITED = 'pipeDelimited'
    DEEP_OBJECT = 'deepObject'
