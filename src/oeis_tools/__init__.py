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
    print(seq.terms[:10])  # Output first 10 terms

For more details, refer to the documentation in individual modules.
"""

# Explicitly import and expose public API to avoid namespace pollution
from .sequence import OEISSequence
from .__version__ import __version__

# Define __all__ for controlled wildcard imports
__all__ = ['OEISSequence']
