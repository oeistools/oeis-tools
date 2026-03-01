# SPDX-License-Identifier: MIT
# Copyright (c) 2025 EnriquePH

"""Tests for ``oeis_tools.sequence.Sequence``."""

from datetime import datetime

import pytest
import requests

from oeis_tools.sequence import Sequence


class DummyResponse:
    """Minimal JSON response object for mocking API calls."""

    def __init__(self, payload, error=None):
        """Store mock payload and optional HTTP error."""
        self._payload = payload
        self._error = error

    def raise_for_status(self):
        """Raise the configured HTTP error when present."""
        if self._error:
            raise self._error
        return None

    def json(self):
        """Return the stored JSON payload."""
        return self._payload


class DummyBFile:
    """Simple placeholder used to avoid network calls in ``Sequence``."""

    def __init__(self, oeis_id):
        """Keep the sequence ID passed by ``Sequence``."""
        self.oeis_id = oeis_id

    def get_filename(self):
        """Provide default b-file filename in tests."""
        return "b000001.txt"

    def get_url(self):
        """Provide default b-file URL in tests."""
        return "https://oeis.org/A000001/b000001.txt"

    def get_bfile_data(self):
        """Default to no parsed b-file data."""
        return None


def test_sequence_parses_json_fields_and_builds_links(monkeypatch):
    """Parse key OEIS fields, datetimes, links, and b-file integration."""
    payload = [
        {
            "id": "M1234 N5678",
            "data": "1,1,2,3,5,8",
            "name": "Fibonacci numbers",
            "comment": ["First comment", "Second comment"],
            "reference": ["Ref A", "Ref B"],
            "formula": ["a(n)=a(n-1)+a(n-2)"],
            "example": ["a(5)=5"],
            "maple": ["seq(fibonacci(n),n=0..10);"],
            "mathematica": ["Table[Fibonacci[n], {n,0,10}]"],
            "program": ["Python: ..."],
            "xref": ["Cf. A000204"],
            "keyword": "nonn",
            "offset": "0,2",
            "author": "_Tom Verhoeff_, _N. J. A. Sloane_",
            "references": ["Some extra reference"],
            "revision": "42",
            "time": "2024-01-02 03:04:05",
            "created": "2000-01-01 00:00:00",
            "link": [
                '<a href="/A000045">Main entry</a>',
                '<a href="https://example.com/ref">External ref</a>',
                'See also <a href="/wiki">wiki</a>',
            ],
        }
    ]

    monkeypatch.setattr("oeis_tools.sequence.requests.get", lambda url, timeout: DummyResponse(payload))
    monkeypatch.setattr("oeis_tools.sequence.BFile", DummyBFile)

    seq = Sequence("A000045")

    assert seq.id == "A000045"
    assert seq.m_id == "M1234"
    assert seq.n_id == "N5678"
    assert seq.name == "Fibonacci numbers"
    assert seq.comment == "First comment\nSecond comment"
    assert seq.reference == "Ref A\nRef B"
    assert seq.author == ["Tom Verhoeff", "N. J. A. Sloane"]
    assert seq.keyword == ["nonn"]
    assert seq.offset == [0, 2]
    assert seq.time == datetime(2024, 1, 2, 3, 4, 5)
    assert seq.created == datetime(2000, 1, 1, 0, 0, 0)
    assert "[Main entry](https://oeis.org/A000045)" in seq.link
    assert "[External ref](https://example.com/ref)" in seq.link
    assert "[wiki](https://oeis.org/wiki)" in seq.link
    assert isinstance(seq.bfile, DummyBFile)
    assert seq.bfile.oeis_id == "A000045"


def test_sequence_rejects_invalid_oeis_id():
    """Raise ``ValueError`` for invalid OEIS identifiers."""
    with pytest.raises(ValueError, match="Invalid OEIS ID"):
        Sequence("invalid-id")


def test_sequence_propagates_http_error(monkeypatch):
    """Propagate HTTP errors from the JSON endpoint."""
    def fake_get(url, timeout):
        return DummyResponse(payload=None, error=requests.HTTPError("request failed"))

    monkeypatch.setattr("oeis_tools.sequence.requests.get", fake_get)

    with pytest.raises(requests.HTTPError, match="request failed"):
        Sequence("A000001")


def test_sequence_author_ignores_trailing_year_tokens(monkeypatch):
    """Drop year-only entries when parsing the OEIS author field."""
    payload = [
        {
            "id": "M0001 N0001",
            "author": "_N. J. A. Sloane_, 1964",
            "link": [],
        }
    ]

    monkeypatch.setattr("oeis_tools.sequence.requests.get", lambda url, timeout: DummyResponse(payload))
    monkeypatch.setattr("oeis_tools.sequence.BFile", DummyBFile)

    seq = Sequence("A000001")
    assert seq.author == ["N. J. A. Sloane"]


def test_sequence_author_ignores_trailing_full_date_tokens(monkeypatch):
    """Drop full date entries when parsing the OEIS author field."""
    payload = [
        {
            "id": "M0001 N0001",
            "author": "_Pierre CAMI_, Apr 28 2012",
            "link": [],
        }
    ]

    monkeypatch.setattr("oeis_tools.sequence.requests.get", lambda url, timeout: DummyResponse(payload))
    monkeypatch.setattr("oeis_tools.sequence.BFile", DummyBFile)

    seq = Sequence("A000001")
    assert seq.author == ["Pierre CAMI"]


def test_sequence_offset_ignores_invalid_tokens(monkeypatch):
    """Parse integer offsets and ignore malformed tokens."""
    payload = [
        {
            "id": "M0001 N0001",
            "offset": "1, bad, -3",
            "link": [],
        }
    ]

    monkeypatch.setattr("oeis_tools.sequence.requests.get", lambda url, timeout: DummyResponse(payload))
    monkeypatch.setattr("oeis_tools.sequence.BFile", DummyBFile)

    seq = Sequence("A000001")
    assert seq.offset == [1, -3]


def test_sequence_keyword_splits_and_ignores_empty_tokens(monkeypatch):
    """Parse keywords into a list and drop empty entries."""
    payload = [
        {
            "id": "M0001 N0001",
            "keyword": "nonn, easy, ,look",
            "link": [],
        }
    ]

    monkeypatch.setattr("oeis_tools.sequence.requests.get", lambda url, timeout: DummyResponse(payload))
    monkeypatch.setattr("oeis_tools.sequence.BFile", DummyBFile)

    seq = Sequence("A000001")
    assert seq.keyword == ["nonn", "easy", "look"]


def test_sequence_get_bfile_info_with_data(monkeypatch):
    """Return metadata and stats when b-file data is available."""
    payload = [{"id": "M0001 N0001", "link": []}]

    class BFileWithData(DummyBFile):
        def get_filename(self):
            return "b000045.txt"

        def get_url(self):
            return "https://oeis.org/A000045/b000045.txt"

        def get_bfile_data(self):
            return [0, 1, 1, 2, 3]

    monkeypatch.setattr("oeis_tools.sequence.requests.get", lambda url, timeout: DummyResponse(payload))
    monkeypatch.setattr("oeis_tools.sequence.BFile", BFileWithData)

    seq = Sequence("A000001")
    info = seq.get_bfile_info()

    assert info["available"] is True
    assert info["filename"] == "b000045.txt"
    assert info["url"] == "https://oeis.org/A000045/b000045.txt"
    assert info["length"] == 5
    assert info["first"] == 0
    assert info["last"] == 3
    assert info["min"] == 0
    assert info["max"] == 3


def test_sequence_get_bfile_info_without_data(monkeypatch):
    """Return unavailable metadata when b-file data is missing."""
    payload = [{"id": "M0001 N0001", "link": []}]

    monkeypatch.setattr("oeis_tools.sequence.requests.get", lambda url, timeout: DummyResponse(payload))
    monkeypatch.setattr("oeis_tools.sequence.BFile", DummyBFile)

    seq = Sequence("A000001")
    info = seq.get_bfile_info()

    assert info["available"] is False
    assert info["filename"] == "b000001.txt"
    assert info["url"] == "https://oeis.org/A000001/b000001.txt"
    assert info["length"] == 0
    assert info["first"] is None
    assert info["last"] is None
    assert info["min"] is None
    assert info["max"] is None


def test_sequence_get_xref_ids_extracts_unique_oeis_ids(monkeypatch):
    """Extract OEIS IDs from multi-line cross-reference text."""
    payload = [
        {
            "id": "M0001 N0001",
            "xref": [
                "Essentially the partial sums of A001468.",
                "Cf. A000201, A001622, A003622, A022342, A026351, A035336, A060143.",
                "Cf. A004919, A004920, A004921, A004922, A004923, A004924, A004925.",
                "Cf. A004926, A004927, A004928, A004929, A004930, A004931, A004932.",
                "Cf. A004933, A004934, A004935, A004976, A090909, A000201.",
            ],
            "link": [],
        }
    ]

    monkeypatch.setattr("oeis_tools.sequence.requests.get", lambda url, timeout: DummyResponse(payload))
    monkeypatch.setattr("oeis_tools.sequence.BFile", DummyBFile)

    seq = Sequence("A000001")
    assert seq.get_xref_ids() == [
        "A001468",
        "A000201",
        "A001622",
        "A003622",
        "A022342",
        "A026351",
        "A035336",
        "A060143",
        "A004919",
        "A004920",
        "A004921",
        "A004922",
        "A004923",
        "A004924",
        "A004925",
        "A004926",
        "A004927",
        "A004928",
        "A004929",
        "A004930",
        "A004931",
        "A004932",
        "A004933",
        "A004934",
        "A004935",
        "A004976",
        "A090909",
    ]


def test_sequence_get_data_values_parses_integer_terms(monkeypatch):
    """Parse OEIS data string into integer values."""
    payload = [
        {
            "id": "M0001 N0001",
            "data": "0,1,1,2,3,5,8,13,21,34",
            "link": [],
        }
    ]

    monkeypatch.setattr("oeis_tools.sequence.requests.get", lambda url, timeout: DummyResponse(payload))
    monkeypatch.setattr("oeis_tools.sequence.BFile", DummyBFile)

    seq = Sequence("A000001")
    assert seq.get_data_values() == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_sequence_get_data_values_ignores_non_numeric_fragments(monkeypatch):
    """Ignore ellipsis and malformed chunks while parsing integers."""
    payload = [
        {
            "id": "M0001 N0001",
            "data": "-2, -1, 0, 1, 2, ..., bad",
            "link": [],
        }
    ]

    monkeypatch.setattr("oeis_tools.sequence.requests.get", lambda url, timeout: DummyResponse(payload))
    monkeypatch.setattr("oeis_tools.sequence.BFile", DummyBFile)

    seq = Sequence("A000001")
    assert seq.get_data_values() == [-2, -1, 0, 1, 2]


def test_sequence_get_keyword_description_returns_lookup_value(monkeypatch):
    """Resolve keyword descriptions through the sequence helper method."""
    payload = [{"id": "M0001 N0001", "keyword": "nonn, easy", "link": []}]

    monkeypatch.setattr("oeis_tools.sequence.requests.get", lambda url, timeout: DummyResponse(payload))
    monkeypatch.setattr("oeis_tools.sequence.BFile", DummyBFile)

    seq = Sequence("A000001")
    assert seq.get_keyword_description("nonn") == (
        "Displayed terms are nonnegative (later terms may still become negative)."
    )
    assert seq.get_keyword_description("easy") == "It is easy to produce terms of this sequence."
    assert seq.get_keyword_description("missing") is None


def test_sequence_get_keyword_description_normalizes_tag_input(monkeypatch):
    """Normalize case/whitespace and handle empty input for keyword lookup."""
    payload = [{"id": "M0001 N0001", "keyword": "nonn, easy", "link": []}]

    monkeypatch.setattr("oeis_tools.sequence.requests.get", lambda url, timeout: DummyResponse(payload))
    monkeypatch.setattr("oeis_tools.sequence.BFile", DummyBFile)

    seq = Sequence("A000001")
    assert seq.get_keyword_description("  EASY ") == "It is easy to produce terms of this sequence."
    assert seq.get_keyword_description("") is None
