# SPDX-License-Identifier: MIT
# Copyright (c) 2025 EnriquePH

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


# A mapping of OEIS keyword tags to their descriptions, based on the OEIS wiki.
# https://oeis.org/wiki/Keywords
OEIS_KEYWORD_DESCRIPTIONS = {
    "base": "Sequence is dependent on the numeral base used.",
    "bref": "Sequence is too short to do any analysis with.",
    "cofr": "A continued fraction expansion of a number.",
    "cons": "A decimal expansion of a number (occasionally another base).",
    "core": "A fundamental sequence.",
    "dead": (
        "An erroneous or duplicated sequence kept with pointers to correct versions."
    ),
    "dumb": "An unimportant sequence.",
    "easy": "It is easy to produce terms of this sequence.",
    "eigen": "An eigensequence: a fixed sequence under some transformation.",
    "fini": "A confirmed finite sequence.",
    "frac": "Numerators or denominators of a sequence of rational numbers.",
    "full": "The full sequence is given (implies the sequence is finite).",
    "hard": "Next term is not known and may be hard to find; more terms are requested.",
    "hear": "Graph audio is considered particularly interesting or beautiful.",
    "less": "Less interesting sequence and less likely to be the intended target.",
    "look": "Graph visual is considered particularly interesting or beautiful.",
    "more": "More terms are needed; extension requested.",
    "mult": "Multiplicative sequence: a(m*n)=a(m)*a(n) for gcd(m,n)=1.",
    "nice": "An exceptionally nice sequence.",
    "nonn": "Displayed terms are nonnegative (later terms may still become negative).",
    "obsc": "Obscure sequence; better description needed.",
    "sign": "Sequence contains negative numbers.",
    "tabf": "Irregular array read row by row.",
    "tabl": "Regular array read row by row.",
    "unkn": "Definition or context is not known.",
    "walk": "Counts walks or self-avoiding paths.",
    "word": "Depends on words in some language.",
    "allocated": "A-number allocated for a contributor; entry not ready to go live.",
    "changed": "Older entry modified within the last two weeks.",
    "new": "New entry, added or modified within roughly the last two weeks.",
    "probation": "Included provisionally and may be deleted at editor discretion.",
    "recycled": "A proposed entry was rejected and the A-number is reused.",
    "uned": "Not edited; entry still needs editorial review.",
}

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
    
    Returns:[print(item[0]) for item in json_dict()]
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
            - 'graph': OEIS graph image URL (PNG).
            - None: Standard webpage URL.
    
    Returns:
        str: The URL.
    """
    formats = {
        "json": f"{OEIS_URL}/search?q=id:{oeis_id}&fmt=json",
        "text": f"{OEIS_URL}/search?q=id:{oeis_id}&fmt=text",
        "bfile": f"{OEIS_URL}/{oeis_id}/{oeis_bfile(oeis_id)}",
        "graph": f"{OEIS_URL}/{oeis_id}/graph?png=1",
        None: f"{OEIS_URL}/{oeis_id}",
    }
    return formats.get(fmt, formats[None])


def oeis_keyword_description(keyword_tag):
    """
    Return the OEIS wiki description for a keyword tag.

    Args:
        keyword_tag (str): OEIS keyword tag, e.g. ``"nonn"``.

    Returns:
        str or None: Keyword description, or ``None`` if the tag is unknown.
    """
    if keyword_tag is None:
        return None
    tag = str(keyword_tag).strip().lower()
    if not tag:
        return None
    return OEIS_KEYWORD_DESCRIPTIONS.get(tag)
