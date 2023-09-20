from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

import pytest

if TYPE_CHECKING:
    from aiohttp.test_utils import TestClient


async def test_aiohttp_integration_valid_input(client: TestClient):
    # Given
    given_query_string = {
        "q": "string",
    }
    given_headers = {
        "content-type": "application/json",
        "Host": "localhost",
    }
    given_data = {"param1": 1}
    expected_status_code = 200
    expected_response_data = {"data": "data"}
    # When
    response = await client.post(
        "/browse/12/",
        params=given_query_string,
        json=given_data,
        headers=given_headers,
    )
    response_data = await response.json()
    # Then
    assert response.status == expected_status_code
    assert response_data == expected_response_data


async def test_aiohttp_integration_invalid_server(client: TestClient, request):
    if "no_validation" in request.node.name:
        pytest.skip("No validation for given handler.")
    # Given
    given_query_string = {
        "q": "string",
    }
    given_headers = {
        "content-type": "application/json",
        "Host": "petstore.swagger.io",
    }
    given_data = {"param1": 1}
    expected_status_code = 400
    expected_response_data = {
        "errors": [
            {
                "message": (
                    "Server not found for "
                    "http://petstore.swagger.io/browse/12/"
                ),
            }
        ]
    }
    # When
    response = await client.post(
        "/browse/12/",
        params=given_query_string,
        json=given_data,
        headers=given_headers,
    )
    response_data = await response.json()
    # Then
    assert response.status == expected_status_code
    assert response_data == expected_response_data


async def test_aiohttp_integration_invalid_input(
    client: TestClient, response_getter, request
):
    if "no_validation" in request.node.name:
        pytest.skip("No validation for given handler.")
    # Given
    given_query_string = {
        "q": "string",
    }
    given_headers = {
        "content-type": "application/json",
        "Host": "localhost",
    }
    given_data = {"param1": "string"}
    response_getter.return_value = {"data": 1}
    expected_status_code = 400
    expected_response_data = {"errors": [{"message": mock.ANY}]}
    # When
    response = await client.post(
        "/browse/12/",
        params=given_query_string,
        json=given_data,
        headers=given_headers,
    )
    response_data = await response.json()
    # Then
    assert response.status == expected_status_code
    assert response_data == expected_response_data
