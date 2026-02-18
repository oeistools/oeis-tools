"""Tests for ``oeis_tools.bfile.BFile``."""

import sys
from types import SimpleNamespace

import pytest
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


def test_bfile_plot_data_plots_values(monkeypatch):
    """Plot parsed b-file values onto a matplotlib-like axes object."""
    class FakeAxes:
        def __init__(self):
            self.plot_calls = []
            self.title = None
            self.xlabel = None
            self.ylabel = None

        def plot(self, x, y, **kwargs):
            self.plot_calls.append((list(x), list(y), kwargs))

        def set_title(self, value):
            self.title = value

        def set_xlabel(self, value):
            self.xlabel = value

        def set_ylabel(self, value):
            self.ylabel = value

    class FakePyplot:
        def __init__(self):
            self.axes = FakeAxes()
            self.show_called = False

        def subplots(self):
            return object(), self.axes

        def show(self):
            self.show_called = True

    fake_pyplot = FakePyplot()
    fake_matplotlib = SimpleNamespace(pyplot=fake_pyplot)

    def fake_get(url, timeout):
        return DummyResponse("0 2\n1 3\n2 5\n")

    monkeypatch.setattr("oeis_tools.bfile.requests.get", fake_get)
    monkeypatch.setitem(sys.modules, "matplotlib", fake_matplotlib)
    monkeypatch.setitem(sys.modules, "matplotlib.pyplot", fake_pyplot)

    bfile = BFile("A000045")
    ax = bfile.plot_data(show=False, color="black")

    assert ax is fake_pyplot.axes
    assert fake_pyplot.axes.plot_calls == [([0, 1, 2], [2, 3, 5], {"color": "black"})]
    assert fake_pyplot.axes.title == "A000045 b-file data"
    assert fake_pyplot.axes.xlabel == "Index"
    assert fake_pyplot.axes.ylabel == "Value"
    assert fake_pyplot.show_called is False


def test_bfile_plot_data_raises_when_data_missing(monkeypatch):
    """Reject plotting when b-file data is unavailable."""
    def fake_get(url, timeout):
        raise requests.RequestException("network error")

    monkeypatch.setattr("oeis_tools.bfile.requests.get", fake_get)

    bfile = BFile("A000045")
    with pytest.raises(ValueError, match="No b-file data available to plot"):
        bfile.plot_data(show=False)
