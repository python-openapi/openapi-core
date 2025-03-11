---
hide:
  - navigation
---

# Contributing

Firstly, thank you for taking the time to contribute.

The following section describes how you can contribute to the openapi-core project on GitHub.

## Reporting bugs

### Before you report

- Check whether your issue already exists in the [Issue tracker](https://github.com/python-openapi/openapi-core/issues).
- Make sure it is not a support request or question better suited for the [Discussion board](https://github.com/python-openapi/openapi-core/discussions).

### How to submit a report

- Include a clear title.
- Describe your runtime environment with the exact versions you use.
- Describe the exact steps to reproduce the problem, including minimal code snippets.
- Describe the behavior you observed after following the steps, including console outputs.
- Describe the expected behavior and why, including links to documentation.

## Code contribution

### Prerequisites

Install [Poetry](https://python-poetry.org) by following the [official installation instructions](https://python-poetry.org/docs/#installation). Optionally (but recommended), configure Poetry to create a virtual environment in a folder named `.venv` within the root directory of the project:

```console
poetry config virtualenvs.in-project true
```

### Setup

To create a development environment and install the runtime and development dependencies, run:

```console
poetry install
```

Then enter the virtual environment created by Poetry:

```console
poetry shell
```

### Static checks

The project uses static checks with the fantastic [pre-commit](https://pre-commit.com/). Every change is checked on CI, and if it does not pass the tests, it cannot be accepted. If you want to check locally, run the following command to install pre-commit.

To enable pre-commit checks for commit operations in git, enter:

```console
pre-commit install
```

To run all checks on your staged files, enter:

```console
pre-commit run
```

To run all checks on all files, enter:

```console
pre-commit run --all-files
```

Pre-commit check results are also attached to your PR through integration with GitHub Actions.
