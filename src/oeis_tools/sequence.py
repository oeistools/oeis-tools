"""Tools and utilities for working with OEIS integer sequences."""

import re
from datetime import datetime
import requests

from .__version__ import __version__
from .utils import check_id, oeis_bfile, oeis_url, OEIS_URL
from .bfile import BFile

class Sequence:
    """
    A class to represent an OEIS sequence, fetching data from the JSON API.
    
    Attributes:
        id (str): The OEIS ID.
        data_json (dict): The JSON data fetched from OEIS for the sequence.
        m_id (str or None): The M ID from the 'id' field (e.g., 'M0692'), or None.
        n_id (str or None): The N ID from the 'id' field (e.g., 'N0256'), or None.
        time (datetime or None): The last modification time from the 'time' field.
        created (datetime or None): The creation time from the 'created' field.
        link (str): Formatted links from the 'link' field as printable text with hyperlinks.
        BFile (BFile or None): The BFile object if available, else None.
        data (str): The sequence data from the 'data' field.
        name (str): The sequence name from the 'name' field.
        comment (str): Comments from the 'comment' field.
        reference (str): References from the 'reference' field.
        formula (str): Formulas from the 'formula' field.
        example (str): Examples from the 'example' field.
        maple (str): Maple code from the 'maple' field.
        mathematica (str): Mathematica code from the 'mathematica' field.
        program (str): Programs from the 'program' field.
        xref (str): Cross-references from the 'xref' field.
        keyword (str): Keywords from the 'keyword' field.
        offset (str): Offset information from the 'offset' field.
        author (str): Author information from the 'author' field.
        references (str): Additional references from the 'references' field.
        revision (str): Revision information from the 'revision' field.
    """

    def __init__(self, oeis_id):
        """
        Initialize the Sequence with the given OEIS ID.
        
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
        self.id = oeis_id

        # Add direct attributes from data_json
        self.data = self.data_json.get('data', '')
        self.name = self.data_json.get('name', '')
        comment_raw = self.data_json.get('comment', [])
        self.comment = ('\n'.join(comment_raw) if isinstance(comment_raw, list)
                       else comment_raw)
        reference_raw = self.data_json.get('reference', [])
        self.reference = ('\n'.join(reference_raw) if isinstance(reference_raw, list)
                         else reference_raw)
        formula_raw = self.data_json.get('formula', [])
        self.formula = ('\n'.join(formula_raw) if isinstance(formula_raw, list)
                       else formula_raw)
        example_raw = self.data_json.get('example', [])
        self.example = ('\n'.join(example_raw) if isinstance(example_raw, list)
                       else example_raw)
        maple_raw = self.data_json.get('maple', [])
        self.maple = ('\n'.join(maple_raw) if isinstance(maple_raw, list)
                     else maple_raw)
        mathematica_raw = self.data_json.get('mathematica', [])
        self.mathematica = ('\n'.join(mathematica_raw) if isinstance(mathematica_raw, list)
                           else mathematica_raw)
        program_raw = self.data_json.get('program', [])
        self.program = ('\n'.join(program_raw) if isinstance(program_raw, list)
                       else program_raw)
        xref_raw = self.data_json.get('xref', [])
        self.xref = ('\n'.join(xref_raw) if isinstance(xref_raw, list)
                    else xref_raw)
        self.keyword = self.data_json.get('keyword', '')
        self.offset = self.data_json.get('offset', '')
        self.author = self.data_json.get('author', '')
        references_raw = self.data_json.get('references', [])
        self.references = ('\n'.join(references_raw) if isinstance(references_raw, list)
                          else references_raw)
        self.revision = self.data_json.get('revision', '')

        # Parse M and N IDs from the 'id' field
        id_str = self.data_json.get('id', '')
        parts = id_str.split() if id_str else []
        self.m_id = parts[0] if parts else None
        self.n_id = parts[1] if len(parts) > 1 else None

        # Parse time and created as datetime objects
        time_str = self.data_json.get('time')
        self.time = datetime.fromisoformat(time_str) if time_str else None
        created_str = self.data_json.get('created')
        self.created = datetime.fromisoformat(created_str) if created_str else None

        # Parse links as formatted text with hyperlinks
        links = self.data_json.get('link', [])
        formatted_links = []
        for link in links:
            # Parse HTML <a href="url">text</a> and convert to Markdown [text](url)
            match = re.search(r'<a href="([^"]*)">(.*?)</a>', link)
            if match:
                url, text = match.groups()
                if url.startswith('/'):
                    url = OEIS_URL + url
                formatted_links.append(f"[{text}]({url})")
            else:
                # If no <a>, just add the text, but replace relative URLs
                formatted_link = re.sub(r'href="/', f'href="{OEIS_URL}/', link)
                formatted_links.append(formatted_link)
        self.link = '\n'.join(formatted_links) if formatted_links else ''

        # Fetch BFile if content if b-file link is present
        self.bfile = BFile(self.id)

__all__ = ["__version__",
            "check_id",
            "oeis_bfile",
            "oeis_url",
            "OEIS_URL",
            "Bfile",
            "Sequence"]
