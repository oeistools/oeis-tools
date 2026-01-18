"""
Utility functions for working with OEIS identifiers and URLs.

This module provides small, self-contained helpers related to the
Online Encyclopedia of Integer Sequences (OEIS), including:

- Validation of OEIS sequence identifiers (e.g. ``A000001``).
- Construction of b-file filenames.
- Generation of OEIS URLs in different formats (web, JSON, text, b-file).

The functions in this module are pure utilities: they perform no network
requests and have no side effects beyond basic validation.
"""

import re

OEIS_URL = "https://oeis.org"

def check_id(oeis_id):
    """
    Check if the OEIS ID is valid.
    It must start with 'A' followed by exactly 6 digits.
    
    Args:
        oeis_id (str): The ID to check.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    pattern = r'^A\d{6}$'
    return bool(re.match(pattern, oeis_id))

def oeis_bfile(oeis_id):
    """
    Generate the b-file filename for a given OEIS ID.
    
    The b-file is a text file containing the sequence data.
    The filename format is 'b' followed by the 6-digit number and '.txt'.
    
    Args:
        oeis_id (str): A valid OEIS ID, e.g., 'A000001'.
    
    Returns:
        str: The b-file filename, e.g., 'b000001.txt'.
    
    Raises:
        ValueError: If the oeis_id is not in the correct format.
    """
    if not check_id(oeis_id):
        raise ValueError(f"Invalid OEIS ID: {oeis_id}")

    # Extract the 6 digits after 'A'
    digits = oeis_id[1:]
    return f"b{digits}.txt"

def oeis_url(oeis_id, fmt=None):
    """
    Generate the OEIS webpage URL for a given OEIS ID.
    
    Args:
        oeis_id (str): The OEIS ID, e.g., 'A000001'.
        fmt (str, optional): The format of the response. 
            - 'json': JSON search URL.
            - 'text': Text search URL.
            - 'bfile': b-file URL.
            - None: Standard webpage URL.
    
    Returns:
        str: The URL.
    """
    formats = {
        "json": f"{OEIS_URL}/search?q=id:{oeis_id}&fmt=json",
        "text": f"{OEIS_URL}/search?q=id:{oeis_id}&fmt=text",
        "bfile": f"{OEIS_URL}/{oeis_id}/{oeis_bfile(oeis_id)}",
        None: f"{OEIS_URL}/{oeis_id}",
    }
    return formats.get(fmt, formats[None])
