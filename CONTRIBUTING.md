# Contributing to oeis-tools

## Development Setup

```bash
git clone https://github.com/oeistools/oeis-tools.git
cd oeis-tools
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Local Checks

Run these checks before opening a pull request:

```bash
ruff format .
ruff check . --fix
pytest -q
python -m build
python -m twine check dist/*
```

## Pull Requests

- Keep PRs focused on one change set.
- Add or update tests for behavioral changes.
- Update `README.md` when user-facing behavior changes.
- Ensure GitHub Actions checks are green.
