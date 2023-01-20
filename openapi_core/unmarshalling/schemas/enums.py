"""OpenAPI core unmarshalling schemas enums module"""
from enum import Enum


class ValidationContext(Enum):
    REQUEST = "request"
    RESPONSE = "response"
