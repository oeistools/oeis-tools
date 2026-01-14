# OEISTools

**OEISTools** is a lightweight toolkit for working with integer sequences from the  
**Online Encyclopedia of Integer Sequences (OEIS)**.

It provides simple, programmatic access to OEIS data and utilities commonly used in
experimental mathematics, number theory, and sequence exploration.

---

## Features

- 🔍 Retrieve sequences by OEIS ID (e.g. `A000045`)
- 📄 Access metadata: name, description, references, comments
- 🔢 Work directly with sequence terms as native vectors/lists
- ⚡ Minimal dependencies, simple API
- 🧩 Designed for exploratory and research workflows

---

## Availability

OEISTools is available for multiple languages:

- **Python** → [`oeis-tools`](https://github.com/oeistools/oeis-tools)
- **R** → [`oeisTools`](https://github.com/oeistools/oeisTools)

Both implementations aim to provide a **similar conceptual API**, adapted to each
language’s conventions.

---

## Python

### Installation

```bash
pip install oeis-tools
```

### Quick example
```
from oeis_tools import get_sequence

seq = get_sequence("A000045")  # Fibonacci numbers
print(seq.values[:10])
```
```