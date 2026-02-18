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
        json (dict): The JSON data fetched from OEIS for the sequence.
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
        keyword (list[str]): Keywords parsed from the 'keyword' field.
        offset (list[int]): Offset values parsed from the 'offset' field.
        author (list[str]): Author names parsed from the 'author' field.
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
        self.json = response.json()[0]
        self.id = oeis_id

        # Add direct attributes from json
        self.data = self.json.get('data', '')
        self.name = self.json.get('name', '')
        comment_raw = self.json.get('comment', [])
        self.comment = ('\n'.join(comment_raw) if isinstance(comment_raw, list)
                       else comment_raw)
        reference_raw = self.json.get('reference', [])
        self.reference = ('\n'.join(reference_raw) if isinstance(reference_raw, list)
                         else reference_raw)
        formula_raw = self.json.get('formula', [])
        self.formula = ('\n'.join(formula_raw) if isinstance(formula_raw, list)
                       else formula_raw)
        example_raw = self.json.get('example', [])
        self.example = ('\n'.join(example_raw) if isinstance(example_raw, list)
                       else example_raw)
        maple_raw = self.json.get('maple', [])
        self.maple = ('\n'.join(maple_raw) if isinstance(maple_raw, list)
                     else maple_raw)
        mathematica_raw = self.json.get('mathematica', [])
        self.mathematica = ('\n'.join(mathematica_raw) if isinstance(mathematica_raw, list)
                           else mathematica_raw)
        program_raw = self.json.get('program', [])
        self.program = ('\n'.join(program_raw) if isinstance(program_raw, list)
                       else program_raw)
        xref_raw = self.json.get('xref', [])
        self.xref = ('\n'.join(xref_raw) if isinstance(xref_raw, list)
                    else xref_raw)
        self.keyword = self._parse_keywords(self.json.get('keyword', ''))
        self.offset = self._parse_offset(self.json.get('offset', ''))
        self.author = self._parse_authors(self.json.get('author', ''))
        references_raw = self.json.get('references', [])
        self.references = ('\n'.join(references_raw) if isinstance(references_raw, list)
                          else references_raw)
        self.revision = self.json.get('revision', '')

        # Parse M and N IDs from the 'id' field
        id_str = self.json.get('id', '')
        parts = id_str.split() if id_str else []
        self.m_id = parts[0] if parts else None
        self.n_id = parts[1] if len(parts) > 1 else None

        # Parse time and created as datetime objects
        time_str = self.json.get('time')
        self.time = datetime.fromisoformat(time_str) if time_str else None
        created_str = self.json.get('created')
        self.created = datetime.fromisoformat(created_str) if created_str else None

        # Parse links as formatted text with hyperlinks
        links = self.json.get('link', [])
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

    def get_bfile_info(self):
        """
        Return summary information about the attached b-file data.

        Returns:
            dict: Metadata and basic stats for b-file values.
        """
        data = self.bfile.get_bfile_data() if self.bfile else None
        if data is None:
            return {
                "available": False,
                "filename": self.bfile.get_filename() if self.bfile else None,
                "url": self.bfile.get_url() if self.bfile else None,
                "length": 0,
                "first": None,
                "last": None,
                "min": None,
                "max": None,
            }

        return {
            "available": True,
            "filename": self.bfile.get_filename(),
            "url": self.bfile.get_url(),
            "length": len(data),
            "first": data[0] if data else None,
            "last": data[-1] if data else None,
            "min": min(data) if data else None,
            "max": max(data) if data else None,
        }

    def get_xref_ids(self):
        """
        Extract OEIS IDs from the parsed cross-reference text.

        Returns:
            list[str]: Unique OEIS IDs (e.g. ``A000045``) in first-seen order.
        """
        xref_text = self.xref or ""
        ids = re.findall(r"A\d{6}", xref_text)
        return list(dict.fromkeys(ids))

    def get_data_values(self):
        """
        Parse the sequence data field into integers.

        Returns:
            list[int]: Values extracted from ``self.data``.
        """
        data_raw = self.data
        if isinstance(data_raw, list):
            tokens = data_raw
        elif isinstance(data_raw, str):
            tokens = re.findall(r"[-+]?\d+", data_raw)
        else:
            return []

        values = []
        for token in tokens:
            try:
                values.append(int(token))
            except (TypeError, ValueError):
                continue
        return values

    @staticmethod
    def _parse_authors(author_raw):
        """
        Parse OEIS author field into a clean list of author names.

        The OEIS author field may include markdown-like underscores for
        emphasis (e.g. ``_Tom Verhoeff_, _N. J. A. Sloane_``). This
        method removes wrapper underscores and returns a list of names.

        Args:
            author_raw (str or list[str]): Raw author value from OEIS JSON.

        Returns:
            list[str]: Cleaned author names.
        """
        if isinstance(author_raw, list):
            chunks = author_raw
        elif isinstance(author_raw, str):
            chunks = author_raw.split(",")
        else:
            return []

        authors = []
        for chunk in chunks:
            name = chunk.strip()
            name = re.sub(r'^_+|_+$', '', name).strip()
            if Sequence._is_date_token(name):
                continue
            if name:
                authors.append(name)
        return authors

    @staticmethod
    def _is_date_token(value):
        """
        Return True when a token is a date-like value, not an author name.

        Examples that should be filtered:
        - ``1964``
        - ``Apr 28 2012``
        - ``Apr 28, 2012``
        - ``2012-04-28``
        """
        if re.fullmatch(r"\d{4}", value):
            return True

        date_patterns = [
            r"[A-Za-z]{3,9}\.? \d{1,2},? \d{4}",
            r"\d{1,2} [A-Za-z]{3,9}\.? \d{4}",
            r"\d{4}-\d{2}-\d{2}",
        ]
        return any(re.fullmatch(pattern, value) for pattern in date_patterns)

    @staticmethod
    def _parse_offset(offset_raw):
        """
        Parse OEIS offset field into a list of integers.

        Typical OEIS values look like ``"0,2"`` and are returned as ``[0, 2]``.
        """
        if isinstance(offset_raw, list):
            tokens = offset_raw
        elif isinstance(offset_raw, str):
            tokens = offset_raw.split(",")
        else:
            return []

        offsets = []
        for token in tokens:
            value = str(token).strip()
            if not value:
                continue
            try:
                offsets.append(int(value))
            except ValueError:
                continue
        return offsets

    @staticmethod
    def _parse_keywords(keyword_raw):
        """
        Parse OEIS keyword field into a list of strings.

        Typical OEIS values look like ``"nonn,easy"`` and are returned as
        ``["nonn", "easy"]``.
        """
        if isinstance(keyword_raw, list):
            tokens = keyword_raw
        elif isinstance(keyword_raw, str):
            tokens = keyword_raw.split(",")
        else:
            return []

        keywords = []
        for token in tokens:
            value = str(token).strip()
            if value:
                keywords.append(value)
        return keywords

__all__ = ["__version__",
            "check_id",
            "oeis_bfile",
            "oeis_url",
            "OEIS_URL",
            "BFile",
            "Sequence"]
