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
	@poetry build

dist-cleanup:
	@rm -rf build dist ${PACKAGE_NAME}.egg-info

dist-upload:
	@poetry publish

test-python:
	@pytest

test-cache-cleanup:
	@rm -rf .pytest_cache

reports-cleanup:
	@rm -rf reports

test-cleanup: test-cache-cleanup reports-cleanup

docs-html:
	python -m mkdocs build --clean --site-dir docs_build --config-file mkdocs.yml

docs-cleanup:
	@rm -rf docs_build

cleanup: dist-cleanup test-cleanup

bench-paths:
	@PYTHONHASHSEED=0 python tests/benchmarks/bench_paths.py --paths 500 --templates-ratio 0.7 --lookups 2000 --output bench-paths.json