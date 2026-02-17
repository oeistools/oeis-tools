"""
oeis_tools: A Python package for reading and manipulating data from OEIS.org.

This package provides an object-oriented interface to fetch, parse, and work with
integer sequences from the Online Encyclopedia of Integer Sequences (OEIS).
It follows PEP 8 style guidelines and emphasizes OOP principles for extensibility.

Key components:
- Sequence: Core class for representing and interacting with OEIS sequences.

Example usage:
    from oeis_tools import Sequence

    seq = Sequence.from_id('A000045')  # Fetch Fibonacci sequence
    print(seq.terms[:12])  # Output first 12 terms

For more details, refer to the documentation in individual modules.
"""

from .__version__ import __version__
from .utils import check_id, oeis_bfile, oeis_url
from .utils import OEIS_URL
from .bfile import BFile
from .sequence import Sequence

__all__ = [
    "__version__",
    "check_id",
    "oeis_bfile",
    "oeis_url",
    "OEIS_URL",
    "BFile",
    "Sequence",
]
