import mock
import pytest
import os
import sys


@pytest.yield_fixture(autouse=True, scope='module')
def django_setup():
    directory = os.path.abspath(os.path.dirname(__file__))
    django_project_dir = os.path.join(directory, 'data')
    sys.path.insert(0, django_project_dir)
    with mock.patch.dict(
        os.environ,
        {
            'DJANGO_SETTINGS_MODULE': 'djangoproject.settings',
        }
    ):
        import django
        django.setup()
        yield
    sys.path.remove(django_project_dir)
