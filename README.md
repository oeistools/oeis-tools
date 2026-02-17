# oeis-tools

[![Tests](https://github.com/oeistools/oeis-tools/actions/workflows/tests.yml/badge.svg)](https://github.com/oeistools/oeis-tools/actions/workflows/tests.yml)
[![PyPI version](https://img.shields.io/pypi/v/oeis-tools.svg?cacheSeconds=60)](https://pypi.org/project/oeis-tools/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Python helpers for the [Online Encyclopedia of Integer Sequences (OEIS)](https://oeis.org/).

## Features

- Validate OEIS IDs like `A000045`
- Build canonical OEIS URLs and b-file names
- Fetch and parse sequence JSON data via `Sequence`
- Fetch and parse b-file numeric values via `BFile`

## Installation

```bash
pip install oeis-tools
```

For local development:

```bash
git clone https://github.com/oeistools/oeis-tools.git
cd oeis-tools
pip install -e ".[dev]"
```

## Quick Start

### Utility Functions

```python
import oeis_tools as ot

print(ot.check_id("A000045"))                # True
print(ot.oeis_bfile("A000045"))              # b000045.txt
print(ot.oeis_url("A000045"))                # https://oeis.org/A000045
print(ot.oeis_url("A000045", fmt="json"))    # https://oeis.org/search?q=id:A000045&fmt=json
```

### Sequence API

```python
from oeis_tools import Sequence

seq = Sequence("A000045")

print(seq.id)         # A000045
print(seq.name)       # Fibonacci numbers
print(seq.data)       # "0,1,1,2,3,5,..."
print(seq.author)     # list[str]
print(seq.keyword)    # list[str]
print(seq.offset)     # list[int]
print(seq.link)       # parsed links as markdown-style text

info = seq.get_bfile_info()
print(info["available"], info["length"])
```

### B-file API

```python
from oeis_tools import BFile

bfile = BFile("A000045")

print(bfile.get_filename())   # b000045.txt
print(bfile.get_url())        # https://oeis.org/A000045/b000045.txt
print(bfile.get_bfile_data()) # list[int] or None
```

## API Summary

- `check_id(oeis_id: str) -> bool`
- `oeis_bfile(oeis_id: str) -> str`
- `oeis_url(oeis_id: str, fmt: str | None = None) -> str`
- `Sequence(oeis_id: str)`
- `Sequence.get_bfile_info() -> dict`
- `BFile(oeis_id: str)`
- `BFile.get_filename() -> str`
- `BFile.get_url() -> str`
- `BFile.get_bfile_data() -> list[int] | None`

## Error Behavior

- `Sequence(...)` raises `ValueError` for invalid IDs.
- `Sequence(...)` propagates HTTP errors from the OEIS JSON endpoint.
- `BFile.get_bfile_data()` returns `None` when a b-file cannot be fetched or parsed.

## Development

Run tests:

```bash
pytest -q
```

Build distributions:

```bash
python -m build
python -m twine check dist/*
```

## Publishing

This repository includes a GitHub Actions publish workflow at `.github/workflows/publish.yml`.

- Automatic publish trigger: GitHub Release `published`
- Manual publish trigger: `workflow_dispatch`
- Upload target: PyPI via trusted publishing (`id-token`)

## License

MIT. See `LICENSE`.
