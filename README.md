# oeis-tools

[![Tests](https://github.com/oeistools/oeis-tools/actions/workflows/tests.yml/badge.svg)](https://github.com/oeistools/oeis-tools/actions/workflows/tests.yml)
[![PyPI version](https://img.shields.io/pypi/v/oeis-tools.svg)](https://pypi.org/project/oeis-tools/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

`oeis-tools` is a Python package for working with the
[Online Encyclopedia of Integer Sequences (OEIS)](https://oeis.org/).

It provides:
- OEIS ID validation
- URL and b-file helpers
- A `Sequence` class for OEIS JSON entries
- A `BFile` class for b-file numeric data

## Installation

From PyPI:

```bash
pip install oeis-tools
```

From source:

```bash
git clone https://github.com/oeistools/oeis-tools.git
cd oeis-tools
pip install -e .
```

Development dependencies (tests):

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
import oeis_tools

# Utilities
print(oeis_tools.check_id("A000001"))              # True
print(oeis_tools.oeis_bfile("A000001"))            # b000001.txt
print(oeis_tools.oeis_url("A000001", fmt="json"))  # https://oeis.org/search?q=id:A000001&fmt=json

# Sequence API
seq = oeis_tools.Sequence("A000045")
print(seq.name)        # Fibonacci numbers
print(seq.data)        # comma-separated terms
print(seq.author)      # list[str]
print(seq.json["id"])  # raw JSON field access

# B-file API
bfile = oeis_tools.BFile("A000045")
print(bfile.get_filename())      # b000045.txt
print(bfile.get_url())           # https://oeis.org/A000045/b000045.txt
print(bfile.get_bfile_data()[:5])
```

## API Overview

- `check_id(oeis_id: str) -> bool`
- `oeis_bfile(oeis_id: str) -> str`
- `oeis_url(oeis_id: str, fmt: str | None = None) -> str`
- `Sequence(oeis_id: str)`
  - Key attributes: `id`, `json`, `name`, `data`, `author`, `link`, `bfile`
- `BFile(oeis_id: str)`
  - Methods: `get_filename()`, `get_url()`, `get_bfile_data()`

## Running Tests

```bash
pytest -q
```

## License

MIT. See `LICENSE`.

## Author

Enrique Pérez Herrero - [energycode.org@gmail.com](mailto:energycode.org@gmail.com)
