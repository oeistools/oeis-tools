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
            "author": "N. J. A. Sloane",
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
    assert seq.keyword == "nonn"
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
