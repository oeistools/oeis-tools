"""Tools and utilities for working with OEIS integer sequences."""

import re
import requests

from .__version__ import __version__

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
    if fmt == "json":
        return f"{OEIS_URL}/search?q=id:{oeis_id}&fmt=json"
    elif fmt == "text":
        return f"{OEIS_URL}/search?q=id:{oeis_id}&fmt=text"
    elif fmt == "bfile":
        return f"{OEIS_URL}/{oeis_id}/{oeis_bfile(oeis_id)}"
    else:
        return f"{OEIS_URL}/{oeis_id}"

class OEISSequence:
    """
    A class to represent an OEIS sequence, fetching data from the JSON API.
    
    Attributes:
        oeis_id (str): The OEIS ID.
        data_json (dict): The JSON data fetched from OEIS for the sequence.
        oeis_m_id (str or None): The M ID from the 'id' field (e.g., 'M0692'), or None.
        oeis_n_id (str or None): The N ID from the 'id' field (e.g., 'N0256'), or None.
    """

    def __init__(self, oeis_id):
        """
        Initialize the OEISSequence with the given OEIS ID.
        
        Args:
            oeis_id (str): The OEIS ID, e.g., 'A000001'.
        
        Raises:
            ValueError: If the oeis_id is invalid.
            requests.HTTPError: If the request fails.
        """
        if not check_id(oeis_id):
            raise ValueError(f"Invalid OEIS ID: {oeis_id}")

        json_url = oeis_url(oeis_id, fmt="json")
        response = requests.get(json_url, timeout=10)
        response.raise_for_status()
        self.data_json = response.json()[0]
        self.oeis_id = oeis_id

        # Parse M and N IDs from the 'id' field
        id_str = self.data_json.get('id', '')
        parts = id_str.split() if id_str else []
        self.oeis_m_id = parts[0] if parts else None
        self.oeis_n_id = parts[1] if len(parts) > 1 else None

__all__ = ["__version__", "check_id", "oeis_bfile", "oeis_url", "OEISSequence"]
