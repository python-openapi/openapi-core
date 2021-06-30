from base64 import b64encode
from json import dumps

from falcon.constants import MEDIA_URLENCODED


class BaseTestFalconProject:

    api_key = '12345'

    @property
    def api_key_encoded(self):
        api_key_bytes = self.api_key.encode('utf8')
        api_key_bytes_enc = b64encode(api_key_bytes)
        return str(api_key_bytes_enc, 'utf8')


class TestPetListResource(BaseTestFalconProject):

    def test_get_no_required_param(self, client):
        headers = {
            'Content-Type': 'application/json',
        }

        response = client.simulate_get(
            '/v1/pets', host='petstore.swagger.io', headers=headers)

        assert response.status_code == 400

    def test_get_valid(self, client):
        headers = {
            'Content-Type': 'application/json',
        }
        query_string = "limit=12"

        response = client.simulate_get(
            '/v1/pets',
            host='petstore.swagger.io', headers=headers,
            query_string=query_string,
        )

        assert response.status_code == 200
        assert response.json == {
            'data': [
                {
                    'id': 12,
                    'name': 'Cat',
                    'ears': {
                        'healthy': True,
                    },
                },
            ],
        }

    def test_post_server_invalid(self, client):
        response = client.simulate_post(
            '/v1/pets',
            host='petstore.swagger.io',
        )

        expected_data = {
            'errors': [
                {
                    'class': (
                        "<class 'openapi_core.templating.paths.exceptions."
                        "ServerNotFound'>"
                    ),
                    'status': 400,
                    'title': (
                        'Server not found for '
                        'http://petstore.swagger.io/v1/pets'
                    ),
                }
            ]
        }
        assert response.status_code == 400
        assert response.json == expected_data

    def test_post_required_header_param_missing(self, client):
        cookies = {'user': 1}
        pet_name = 'Cat'
        pet_tag = 'cats'
        pet_street = 'Piekna'
        pet_city = 'Warsaw'
        pet_healthy = False
        data_json = {
            'name': pet_name,
            'tag': pet_tag,
            'position': 2,
            'address': {
                'street': pet_street,
                'city': pet_city,
            },
            'healthy': pet_healthy,
            'wings': {
                'healthy': pet_healthy,
            }
        }
        content_type = 'application/json'
        headers = {
            'Authorization': 'Basic testuser',
            'Content-Type': content_type,
        }
        body = dumps(data_json)

        response = client.simulate_post(
            '/v1/pets',
            host='staging.gigantic-server.com', headers=headers,
            body=body, cookies=cookies, protocol='https',
        )

        expected_data = {
            'errors': [
                {
                    'class': (
                        "<class 'openapi_core.exceptions."
                        "MissingRequiredParameter'>"
                    ),
                    'status': 400,
                    'title': 'Missing required parameter: api-key',
                }
            ]
        }
        assert response.status_code == 400
        assert response.json == expected_data

    def test_post_media_type_invalid(self, client):
        cookies = {'user': 1}
        data = 'data'
        # noly 3 media types are supported by falcon by default:
        # json, multipart and urlencoded
        content_type = MEDIA_URLENCODED
        headers = {
            'Authorization': 'Basic testuser',
            'Api-Key': self.api_key_encoded,
            'Content-Type': content_type,
        }

        response = client.simulate_post(
            '/v1/pets',
            host='staging.gigantic-server.com', headers=headers,
            body=data, cookies=cookies, protocol='https',
        )

        expected_data = {
            'errors': [
                {
                    'class': (
                        "<class 'openapi_core.templating.media_types."
                        "exceptions.MediaTypeNotFound'>"
                    ),
                    'status': 415,
                    'title': (
                        "Content for the following mimetype not found: "
                        f"{content_type}. "
                        "Valid mimetypes: ['application/json', 'text/plain']"
                    ),
                }
            ]
        }
        assert response.status_code == 415
        assert response.json == expected_data

    def test_post_required_cookie_param_missing(self, client):
        content_type = 'application/json'
        data_json = {
            'id': 12,
            'name': 'Cat',
            'ears': {
                'healthy': True,
            },
        }
        headers = {
            'Authorization': 'Basic testuser',
            'Api-Key': self.api_key_encoded,
            'Content-Type': content_type,
        }
        body = dumps(data_json)

        response = client.simulate_post(
            '/v1/pets',
            host='staging.gigantic-server.com', headers=headers,
            body=body, protocol='https',
        )

        expected_data = {
            'errors': [
                {
                    'class': (
                        "<class 'openapi_core.exceptions."
                        "MissingRequiredParameter'>"
                    ),
                    'status': 400,
                    'title': "Missing required parameter: user",
                }
            ]
        }
        assert response.status_code == 400
        assert response.json == expected_data

    def test_post_valid(self, client):
        cookies = {'user': 1}
        content_type = 'application/json'
        data_json = {
            'id': 12,
            'name': 'Cat',
            'ears': {
                'healthy': True,
            },
        }
        headers = {
            'Authorization': 'Basic testuser',
            'Api-Key': self.api_key_encoded,
            'Content-Type': content_type,
        }
        body = dumps(data_json)

        response = client.simulate_post(
            '/v1/pets',
            host='staging.gigantic-server.com', headers=headers,
            body=body, cookies=cookies, protocol='https',
        )

        assert response.status_code == 201
        assert not response.content


class TestPetDetailResource:

    def test_get_server_invalid(self, client):
        headers = {'Content-Type': 'application/json'}

        response = client.simulate_get('/v1/pets/12', headers=headers)

        expected_data = {
            'errors': [
                {
                    'class': (
                        "<class 'openapi_core.templating.paths.exceptions."
                        "ServerNotFound'>"
                    ),
                    'status': 400,
                    'title': (
                        'Server not found for '
                        'http://falconframework.org/v1/pets/12'
                    ),
                }
            ]
        }
        assert response.status_code == 400
        assert response.json == expected_data

    def test_get_path_invalid(self, client):
        headers = {'Content-Type': 'application/json'}

        response = client.simulate_get(
            '/v1/pet/invalid', host='petstore.swagger.io', headers=headers)

        assert response.status_code == 404

    def test_get_unauthorized(self, client):
        headers = {'Content-Type': 'application/json'}

        response = client.simulate_get(
            '/v1/pets/12', host='petstore.swagger.io', headers=headers)

        expected_data = {
            'errors': [
                {
                    'class': (
                        "<class 'openapi_core.validation.exceptions."
                        "InvalidSecurity'>"
                    ),
                    'status': 403,
                    'title': 'Security not valid for any requirement',
                }
            ]
        }
        assert response.status_code == 403
        assert response.json == expected_data

    def test_get_valid(self, client):
        auth = 'authuser'
        content_type = 'application/json'
        headers = {
            'Authorization': f'Basic {auth}',
            'Content-Type': content_type,
        }

        response = client.simulate_get(
            '/v1/pets/12', host='petstore.swagger.io', headers=headers)

        assert response.status_code == 200

    def test_delete_method_invalid(self, client):
        auth = 'authuser'
        content_type = 'application/json'
        headers = {
            'Authorization': f'Basic {auth}',
            'Content-Type': content_type,
        }

        response = client.simulate_delete(
            '/v1/pets/12', host='petstore.swagger.io', headers=headers)

        expected_data = {
            'errors': [
                {
                    'class': (
                        "<class 'openapi_core.templating.paths.exceptions."
                        "OperationNotFound'>"
                    ),
                    'status': 405,
                    'title': (
                        'Operation delete not found for '
                        'http://petstore.swagger.io/v1/pets/12'
                    ),
                }
            ]
        }
        assert response.status_code == 405
        assert response.json == expected_data
