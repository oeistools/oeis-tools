# oeis-tools

**oeis-tools** is a Python package providing utilities for working with the Online Encyclopedia of Integer Sequences (OEIS).

It offers functions to validate OEIS IDs, generate b-file filenames, and construct OEIS URLs for different formats.

## Installation

Install from PyPI:

```bash
pip install oeis-tools
```

Or install from source:

```bash
git clone https://github.com/oeistools/oeis-tools.git
cd oeis-tools
pip install .
```

## Usage

Import the package and use the functions:

```python
import oeis_tools

# Validate an OEIS ID
print(oeis_tools.check_id("A000001"))  # True

# Generate b-file filename
print(oeis_tools.oeis_bfile("A000001"))  # b000001.txt

# Generate OEIS URL
print(oeis_tools.oeis_url("A000001"))  # https://oeis.org/A000001
print(oeis_tools.oeis_url("A000001", fmt="json"))  # https://oeis.org/search?q=id:A000001&fmt=json
```

## Functions

- `check_id(oeis_id)`: Validates if the given string is a valid OEIS ID (starts with 'A' followed by 6 digits).
- `oeis_bfile(oeis_id)`: Returns the b-file filename for the given OEIS ID.
- `oeis_url(oeis_id, fmt=None)`: Generates the OEIS URL. `fmt` can be 'json', 'text', 'bfile', or None for the main page.

## Classes

- `OEISSequence(oeis_id)`: A class that fetches and stores the JSON data for the given OEIS ID in the `data_json` attribute (as a dict). Also provides parsed attributes: `oeis_m_id`, `oeis_n_id` (or None), `oeis_time`, `oeis_created` (as datetime objects), `oeis_link` (formatted links as Markdown), and `bfile` (text content of the b-file if available).

Example:

```python
seq = oeis_tools.OEISSequence("A000045")
print(seq.data_json['name'])  # Fibonacci numbers...
print(seq.bfile.split('\n')[0])  # First line of b-file
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Enrique Pérez Herrero - [energycode.org@gmail.com](mailto:energycode.org@gmail.com)
```