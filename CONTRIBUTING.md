
Contributor Guide
=================

# Static checks

The project uses static checks using fantastic [pre-commit](https://pre-commit.com/). Every change is checked on CI and if it does not pass the tests it cannot be accepted. If you want to check locally then run following command to install pre-commit:

```bash
pip install -r requiremenets_dev.txt
```

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
