# oeis-tools

A focused Python toolkit for working with OEIS integer sequences: fetch metadata, parse b-files, and plot sequence values quickly.

## Overview

Welcome to the `oeis-tools` documentation. This library allows you to interact with the Online Encyclopedia of Integer Sequences (OEIS) programmatically.

- **Fast & Lightweight:** Fetch sequence metadata and data without bloat.
- **Plotting:** Built-in `matplotlib` integration for visualizing sequence data.
- **Robust:** Includes utilities to parse and cache `b-files`.

## Quick Start

```bash
pip install oeis-tools
```

```python
import oeis_tools as ot

seq = ot.Sequence("A000045")
print(seq.name)  # Fibonacci numbers
```

Check out the [Usage Guide](usage.md) for plotting examples and the [API Reference](reference/sequence.md) to see all the available classes and functions.
