class TestPetListResource:

    def test_no_required_param(self, client):
        headers = {
            'Content-Type': 'application/json',
        }

        response = client.simulate_get(
            '/v1/pets', host='petstore.swagger.io', headers=headers)

        assert response.status_code == 400

    def test_valid(self, client):
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


class TestPetDetailResource:

    def test_invalid_path(self, client):
        headers = {'Content-Type': 'application/json'}

        response = client.simulate_get(
            '/v1/pet/invalid', host='petstore.swagger.io', headers=headers)

        assert response.status_code == 404

    def test_invalid_security(self, client):
        headers = {'Content-Type': 'application/json'}

        response = client.simulate_get(
            '/v1/pets/12', host='petstore.swagger.io', headers=headers)

        assert response.status_code == 400

    def test_valid(self, client):
        auth = 'authuser'
        headers = {
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/json',
        }

        response = client.simulate_get(
            '/v1/pets/12', host='petstore.swagger.io', headers=headers)

        assert response.status_code == 200
