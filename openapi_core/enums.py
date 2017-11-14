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


class SchemaType(Enum):

    INTEGER = 'integer'
    NUMBER = 'number'
    STRING = 'string'
    BOOLEAN = 'boolean'
    ARRAY = 'array'
    OBJECT = 'object'


class SchemaFormat(Enum):

    NONE = None
    INT32 = 'int32'
    INT64 = 'int64'
    FLOAT = 'float'
    DOUBLE = 'double'
    BYTE = 'byte'
    BINARY = 'binary'
    DATE = 'date'
    DATETIME = 'date-time'
    PASSWORD = 'password'
