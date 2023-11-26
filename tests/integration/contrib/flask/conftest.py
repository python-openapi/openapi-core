import pytest
from flask import Flask


@pytest.fixture(scope="session")
def schema_path(schema_path_factory):
    specfile = "contrib/flask/data/v3.0/flask_factory.yaml"
    return schema_path_factory.from_file(specfile)


@pytest.fixture
def app(app_factory):
    return app_factory()


@pytest.fixture
def client(client_factory, app):
    return client_factory(app)


@pytest.fixture(scope="session")
def client_factory():
    def create(app):
        return app.test_client()

    return create


@pytest.fixture(scope="session")
def app_factory():
    def create(root_path=None):
        app = Flask("__main__", root_path=root_path)
        app.config["DEBUG"] = True
        app.config["TESTING"] = True
        return app

    return create
