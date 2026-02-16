"""Tests for ``oeis_tools.bfile.BFile``."""

import requests

from oeis_tools.bfile import BFile


class DummyResponse:
    """Minimal response object used to mock ``requests.get``."""

    def __init__(self, text):
        """Store raw text returned by the fake request."""
        self.text = text

    def raise_for_status(self):
        """Mimic a successful HTTP response."""
        return None


def test_bfile_parses_numeric_values_and_metadata(monkeypatch):
    """Parse b-file values and expose expected filename and URL."""
    def fake_get(url, timeout):
        assert "A000045" in url
        assert timeout == 10
        return DummyResponse("# comment\n0 0\n1 1\n2 1\n3 2\n")

    monkeypatch.setattr("oeis_tools.bfile.requests.get", fake_get)

    bfile = BFile("A000045")

    assert bfile.get_filename() == "b000045.txt"
    assert bfile.get_url() == "https://oeis.org/A000045/b000045.txt"
    assert bfile.get_bfile_data() == [0, 1, 1, 2]


def test_bfile_returns_none_when_request_fails(monkeypatch):
    """Return ``None`` when the HTTP request fails."""
    def fake_get(url, timeout):
        raise requests.RequestException("network error")

    monkeypatch.setattr("oeis_tools.bfile.requests.get", fake_get)

    bfile = BFile("A000045")
    assert bfile.get_bfile_data() is None


def test_bfile_returns_none_for_malformed_line(monkeypatch):
    """Return ``None`` when a b-file line cannot be parsed."""
    def fake_get(url, timeout):
        return DummyResponse("0 0\nthis-is-not-valid\n")

    monkeypatch.setattr("oeis_tools.bfile.requests.get", fake_get)

    bfile = BFile("A000045")
    assert bfile.get_bfile_data() is None
