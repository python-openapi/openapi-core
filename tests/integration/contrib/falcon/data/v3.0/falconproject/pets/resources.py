from json import dumps

from falcon.constants import MEDIA_JSON
from falcon.status_codes import HTTP_200, HTTP_201


class PetListResource:
    def on_get(self, request, response):
        assert request.openapi
        assert not request.openapi.errors
        assert request.openapi.parameters.query == {
            'page': 1,
            'limit': 12,
            'search': '',
        }
        data = [
            {
                'id': 12,
                'name': 'Cat',
                'ears': {
                    'healthy': True,
                },
            },
        ]
        response.status = HTTP_200
        response.content_type = MEDIA_JSON
        response.text = dumps({"data": data})
        response.set_header('X-Rate-Limit', '12')

    def on_post(self, request, response):
        assert request.openapi
        assert not request.openapi.errors
        assert request.openapi.parameters.cookie == {
            'user': 1,
        }
        assert request.openapi.parameters.header == {
            'api-key': '12345',
        }
        assert request.openapi.body.__class__.__name__ == 'PetCreate'
        assert request.openapi.body.name == 'Cat'
        assert request.openapi.body.ears.__class__.__name__ == 'Ears'
        assert request.openapi.body.ears.healthy is True

        response.status = HTTP_201
        response.set_header('X-Rate-Limit', '12')


class PetDetailResource:
    def on_get(self, request, response, petId=None):
        assert petId == '12'
        assert request.openapi
        assert not request.openapi.errors
        assert request.openapi.parameters.path == {
            'petId': 12,
        }
        data = {
            'id': 12,
            'name': 'Cat',
            'ears': {
                'healthy': True,
            },
        }
        response.status = HTTP_200
        response.content_type = MEDIA_JSON
        response.text = dumps({"data": data})
        response.set_header('X-Rate-Limit', '12')
