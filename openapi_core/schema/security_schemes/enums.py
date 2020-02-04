"""OpenAPI core security schemes enums module"""
from enum import Enum


class SecuritySchemeType(Enum):

    API_KEY = 'apiKey'
    HTTP = 'http'
    OAUTH2 = 'oauth2'
    OPEN_ID_CONNECT = 'openIdConnect'


class ApiKeyLocation(Enum):

    QUERY = 'query'
    HEADER = 'header'
    COOKIE = 'cookie'

    @classmethod
    def has_value(cls, value):
        return (any(value == item.value for item in cls))


class HttpAuthScheme(Enum):

    BASIC = 'basic'
    BEARER = 'bearer'
