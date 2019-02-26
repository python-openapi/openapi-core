"""OpenAPI core schemas enums module"""
from enum import Enum


class SchemaType(Enum):

    ANY = None
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
    UUID = 'uuid'
