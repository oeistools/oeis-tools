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
    result = bfile.plot_data(show=False, color="black")

    assert result is None
    assert fake_pyplot.axes.plot_calls == [([0, 1, 2], [2, 3, 5], {"color": "black"})]
    assert fake_pyplot.axes.title == "A000045 b-file data"
    assert fake_pyplot.axes.xlabel == "n"
    assert fake_pyplot.axes.ylabel == "Value"
    assert fake_pyplot.show_called is False


def test_bfile_plot_data_uses_bfile_indices_for_x_axis(monkeypatch):
    """Use parsed b-file indices as x values when available."""
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

        def subplots(self):
            return object(), self.axes

        def show(self):
            return None

    fake_pyplot = FakePyplot()
    fake_matplotlib = SimpleNamespace(pyplot=fake_pyplot)

    def fake_get(url, timeout):
        return DummyResponse("10 2\n20 3\n40 5\n")

    monkeypatch.setattr("oeis_tools.bfile.requests.get", fake_get)
    monkeypatch.setitem(sys.modules, "matplotlib", fake_matplotlib)
    monkeypatch.setitem(sys.modules, "matplotlib.pyplot", fake_pyplot)

    bfile = BFile("A000045")
    result = bfile.plot_data(show=False)

    assert result is None
    assert fake_pyplot.axes.plot_calls == [([10, 20, 40], [2, 3, 5], {})]
    assert fake_pyplot.axes.xlabel == "n"


def test_bfile_plot_data_accepts_n_for_prefix_plot(monkeypatch):
    """Plot only the first ``n`` b-file points when requested."""

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

        def subplots(self):
            return object(), self.axes

        def show(self):
            return None

    fake_pyplot = FakePyplot()
    fake_matplotlib = SimpleNamespace(pyplot=fake_pyplot)

    def fake_get(url, timeout):
        return DummyResponse("10 2\n20 3\n40 5\n80 8\n")

    monkeypatch.setattr("oeis_tools.bfile.requests.get", fake_get)
    monkeypatch.setitem(sys.modules, "matplotlib", fake_matplotlib)
    monkeypatch.setitem(sys.modules, "matplotlib.pyplot", fake_pyplot)

    bfile = BFile("A000045")
    result = bfile.plot_data(2, show=False)

    assert result is None
    assert fake_pyplot.axes.plot_calls == [([10, 20], [2, 3], {})]


def test_bfile_plot_data_rejects_invalid_n(monkeypatch):
    """Validate ``n`` type and bounds for plotting."""

    def fake_get(url, timeout):
        return DummyResponse("0 2\n1 3\n")

    monkeypatch.setattr("oeis_tools.bfile.requests.get", fake_get)

    bfile = BFile("A000045")

    with pytest.raises(TypeError, match="n must be an integer or None"):
        bfile.plot_data("2", show=False)

    with pytest.raises(ValueError, match="n must be non-negative"):
        bfile.plot_data(-1, show=False)


def test_bfile_plot_data_raises_when_data_missing(monkeypatch):
    """Reject plotting when b-file data is unavailable."""
    def fake_get(url, timeout):
        raise requests.RequestException("network error")

    monkeypatch.setattr("oeis_tools.bfile.requests.get", fake_get)

    bfile = BFile("A000045")
    with pytest.raises(ValueError, match="No b-file data available to plot"):
        bfile.plot_data(show=False)


def test_bfile_plot_data_uses_log10_for_very_large_values(monkeypatch):
    """Fallback to signed log10 plotting when values exceed float range."""
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
        return DummyResponse("0 0\n1 2\n2 -3\n3 1" + "0" * 400 + "\n")

    monkeypatch.setattr("oeis_tools.bfile.requests.get", fake_get)
    monkeypatch.setitem(sys.modules, "matplotlib", fake_matplotlib)
    monkeypatch.setitem(sys.modules, "matplotlib.pyplot", fake_pyplot)

    bfile = BFile("A000045")
    result = bfile.plot_data(show=False, color="blue")

    assert result is None
    assert fake_pyplot.axes.plot_calls[0][0] == [0, 1, 2, 3]
    assert fake_pyplot.axes.plot_calls[0][1] == pytest.approx([0.0, 0.30103, -0.477121, 400.0], rel=1e-6)
    assert fake_pyplot.axes.plot_calls[0][2] == {"color": "blue"}
    assert fake_pyplot.axes.title == "A000045 b-file data (log10 magnitude)"
    assert fake_pyplot.axes.xlabel == "n"
    assert fake_pyplot.axes.ylabel == "sign(value) * log10(|value|)"


def test_bfile_plot_data_can_return_axes_when_requested(monkeypatch):
    """Return axes only when ``return_ax=True`` is passed."""

    class FakeAxes:
        def __init__(self):
            self.plot_calls = []

        def plot(self, x, y, **kwargs):
            self.plot_calls.append((list(x), list(y), kwargs))

        def set_title(self, value):
            return None

        def set_xlabel(self, value):
            return None

        def set_ylabel(self, value):
            return None

    class FakePyplot:
        def __init__(self):
            self.axes = FakeAxes()

        def subplots(self):
            return object(), self.axes

        def show(self):
            return None

    fake_pyplot = FakePyplot()
    fake_matplotlib = SimpleNamespace(pyplot=fake_pyplot)

    def fake_get(url, timeout):
        return DummyResponse("0 2\n1 3\n2 5\n")

    monkeypatch.setattr("oeis_tools.bfile.requests.get", fake_get)
    monkeypatch.setitem(sys.modules, "matplotlib", fake_matplotlib)
    monkeypatch.setitem(sys.modules, "matplotlib.pyplot", fake_pyplot)

    bfile = BFile("A000045")
    ax = bfile.plot_data(show=False, return_ax=True)

    assert ax is fake_pyplot.axes
