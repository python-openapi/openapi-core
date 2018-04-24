import json

import pytest
import requests
import requests_mock

from openapi_core.wrappers import RequestsFactory
from openapi_core.shortcuts import create_spec
from openapi_core.validators import ResponseValidator, RequestValidator


@pytest.fixture(scope='session', autouse=True)
def create_mock_session():
    session = requests.Session()
    adapter = requests_mock.Adapter()
    session.mount('mock', adapter)


@pytest.fixture(scope='session')
def server_spec(factory):
    server_spec_dict = factory.spec_from_file("data/v3.0/server_path_variations.yaml")
    return create_spec(server_spec_dict)


@pytest.fixture(scope='session')
def spec_dict(factory):
    return factory.spec_from_file("data/v3.0/petstore.yaml")


@pytest.fixture(scope='session')
def spec(spec_dict):
    return create_spec(spec_dict)


@pytest.fixture(scope='session')
def request_validator(spec):
    return RequestValidator(spec)


@pytest.fixture(scope='session')
def response_validator(spec):
    return ResponseValidator(spec)


@pytest.fixture(scope='session')
def server_request_validator(server_spec):
    return RequestValidator(server_spec)


@pytest.fixture
def requests_factory(spec):
    return RequestsFactory(spec)


@pytest.fixture
def server_requests_factory(server_spec):
    return RequestsFactory(server_spec)


def test_mock_get_request_converts_correctly(requests_factory):
    """
    Verifies that a GET request is correctly converted.

    :param requests_factory:
    :type requests_factory: openapi_core.wrappers.RequestsFactory
    """
    with requests_mock.mock() as m:
        m.get('http://petstore.swagger.io/v1/pets/12345?format=json',
              text='{"name": "Sparky"}',
              headers={'Authentication': 'Bearer 123456',
                       'Content-Type': 'application/json'},
              cookies={}
              )
        response = requests.get(url='http://petstore.swagger.io/v1/pets/12345?format=json',
                                headers={'Authorization': 'Bearer 123456',
                                         'Accept': 'application/json'})
        request = requests_factory.create_request(response.request)

        assert request.host_url == "http://petstore.swagger.io/v1"
        assert request.path == "/pets/12345"
        assert request.method == 'get'
        assert request.path_pattern == "/pets/{petId}"
        assert request.parameters['path']['petId'] == '12345'
        assert request.parameters['query']['format'] == ['json']
        assert request.parameters['headers']['Authorization'] == 'Bearer 123456'
        assert not request.parameters['cookies']
        assert not request.body
        assert request.mimetype == 'application/json'

        response = requests_factory.create_response(response)
        assert response.data == '{"name": "Sparky"}'
        assert response.status_code == 200
        assert response.mimetype == 'application/json'


def test_mock_post_request_converts_correctly(requests_factory):
    """
    Verifies that a POST request is correctly converted.

    :param requests_factory:
    :type requests_factory: openapi_core.wrappers.RequestsFactory
    """
    with requests_mock.mock() as m:
        m.post('http://petstore.swagger.io/v1/pets/12345?format=json',
               text='{"name": "Sparky"}',
               headers={'Authentication': 'Bearer 123456',
                        'Content-Type': 'application/json'},
               cookies={}
               )
        response = requests.post(url='http://petstore.swagger.io/v1/pets/12345?format=json',
                                 headers={'Authorization': 'Bearer 123456',
                                          'Accept': 'application/json'},
                                 data='{"name": "Sparky"}'
                                 )
        request = requests_factory.create_request(response.request)

        assert request.host_url == "http://petstore.swagger.io/v1"
        assert request.path == "/pets/12345"
        assert request.method == 'post'
        assert request.path_pattern == "/pets/{petId}"
        assert request.parameters['path']['petId'] == '12345'
        assert request.parameters['query']['format'] == ['json']
        assert request.parameters['headers']['Authorization'] == 'Bearer 123456'
        assert not request.parameters['cookies']
        assert request.body == '{"name": "Sparky"}'
        assert request.mimetype == 'application/json'

        response = requests_factory.create_response(response)
        assert response.data == '{"name": "Sparky"}'
        assert response.status_code == 200
        assert response.mimetype == 'application/json'


def test_server_regex_for_server_wildcards(server_requests_factory, server_request_validator):
    with requests_mock.mock() as m:
        m.get('https://123456.saas-app.com:443/v2/status')
        response = requests.get(url='https://123456.saas-app.com:443/v2/status')
        request = server_requests_factory.create_request(response.request)
        assert request._server_pattern == 'https://(.*).saas-app.com:(443|8443)/v2'
        server_request_validator.validate(request)


def test_get_validation(requests_factory, request_validator, response_validator):
    """
    Verifies that a GET request is correctly converted.

    :param requests_factory:
    :type requests_factory: openapi_core.wrappers.RequestsFactory
    :param request_validator:
    :type request_validator: openapi_core.validators.RequestValidator
    """

    mock_resp = {
        "data": {
            "id": 12345,
            "name": "Sparky",
            "tag": "dogs",
            "address": "1234 Someplace",
            "position": 1

        }
    }
    with requests_mock.mock() as m:
        m.get('http://petstore.swagger.io/v1/pets/12345',
              text=json.dumps(mock_resp),
              headers={'Authentication': 'Bearer 123456',
                       'Content-Type': 'application/json'},
              cookies={}
              )
        response = requests.get(url='http://petstore.swagger.io/v1/pets/12345',
                                headers={'Authorization': 'Bearer 123456',
                                         'Accept': 'application/json'})
        request = requests_factory.create_request(response.request)
        request_validator.validate(request)

        response = requests_factory.create_response(response)
        response_validator.validate(request, response)


def test_post_validation(requests_factory, request_validator, response_validator):
    """
    Verifies that a POST request is correctly validated.

    :param requests_factory:
    :type requests_factory: openapi_core.wrappers.RequestsFactory
    :param request_validator:
    :type request_validator: openapi_core.validators.RequestValidator
    """
    mock_resp = {
        "data": {
            "id": 12345,
            "name": "Sparky",
            "tag": "dogs",
            "address": "1234 Someplace",
            "position": 1,
            "healthy": True

        }
    }
    mock_body = {
        "tag": "dogs",
        "address": "1234 Someplace",
        "position": 1,
        "healthy": True
    }
    with requests_mock.mock() as m:
        m.post('http://petstore.swagger.io/v1/pets',
               text=json.dumps(mock_resp),
               headers={'Authentication': 'Bearer 123456',
                        'Content-Type': 'application/json'},
               cookies={}
               )
        response = requests.post(url='http://petstore.swagger.io/v1/pets',
                                 headers={'Authorization': 'Bearer 123456',
                                          'Accept': 'application/json'},
                                 data=json.dumps(mock_body))
        request = requests_factory.create_request(response.request)
        errors = request_validator.validate(request)
        assert not errors

        response = requests_factory.create_response(response)
        errors = response_validator.validate(request, response)
        assert not errors
