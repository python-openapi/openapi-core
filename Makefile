.EXPORT_ALL_VARIABLES:

PROJECT_NAME=openapi-core
PACKAGE_NAME=$(subst -,_,${PROJECT_NAME})
VERSION=`git describe --abbrev=0`

PYTHONDONTWRITEBYTECODE=1

params:
	@echo "Project name: ${PROJECT_NAME}"
	@echo "Package name: ${PACKAGE_NAME}"
	@echo "Version: ${VERSION}"

dist-build:
	@python setup.py bdist_wheel

dist-cleanup:
	@rm -rf build dist ${PACKAGE_NAME}.egg-info

dist-upload:
	@twine upload dist/*.whl

test-python:
	@python setup.py test

test-cache-cleanup:
	@rm -rf .pytest_cache

reports-cleanup:
	@rm -rf reports

test-cleanup: test-cache-cleanup reports-cleanup

docs-html:
	sphinx-build -b html docs docs/_build

docs-cleanup:
	@rm -rf docs/_build

cleanup: dist-cleanup test-cleanup
