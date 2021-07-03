# Contributor Guide

## Prerequisites

Install [Poetry](https://github.com/python-poetry/poetry) by following the [official installation instructions](https://github.com/python-poetry/poetry#installation). Optionally (but recommended), configure Poetry to create a virtual environment in a folder named `.venv` within the root directory of the project:

```bash
poetry config virtualenvs.in-project true
```

## Setup

To create a development environment and install the runtime and development dependencies, run:

```bash
poetry install
```

Then enter the virtual environment created by Poetry:

```bash
poetry shell
```

## Static checks

The project uses static checks using fantastic [pre-commit](https://pre-commit.com/). Every change is checked on CI and if it does not pass the tests it cannot be accepted. If you want to check locally then run following command to install pre-commit.

To turn on pre-commit checks for commit operations in git, enter:

```bash
pre-commit install
```

To run all checks on your staged files, enter:

```bash
pre-commit run
```

To run all checks on all files, enter:

```bash
pre-commit run --all-files
```

Pre-commit check results are also attached to your PR through integration with Github Action.
