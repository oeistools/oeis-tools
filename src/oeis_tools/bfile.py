"""
Utilities for working with OEIS b-files.

This module provides the BFile class, which represents an OEIS b-file
associated with an integer sequence. A b-file contains sequence values
in the format "n a(n)", one pair per line.

The BFile class handles:
- construction of b-file filenames and URLs
- downloading b-files from the OEIS website
- parsing numeric sequence data

Typical usage:
    >>> from oeis_tools.bfile import BFile
    >>> bfile = BFile("A000045")
    >>> bfile.get_bfile_data()
"""

import requests
from .utils import oeis_bfile, oeis_url


class BFile:
    """
    Represents an OEIS b-file and provides access to its numeric data.

    A b-file contains values of an integer sequence in the form:
    n a(n), one pair per line. This class fetches the b-file from
    the OEIS website and parses its contents into a list of integers.

    Attributes:
        oeis_id (str): The OEIS identifier (e.g., 'A000045').
        filename (str): The b-file name (e.g., 'bA000045.txt').
        url (str): The URL where the b-file can be downloaded.
        bfile_data (list[int] or None): Parsed sequence values from the
            b-file, or None if the b-file could not be retrieved or parsed.
    """

    def __init__(self, oeis_id):
        self.oeis_id = oeis_id
        self.filename = oeis_bfile(oeis_id)
        self.url = oeis_url(oeis_id, fmt="bfile")
        self.data = self.fetch_bfile_data()

    def fetch_bfile_data(self):
        """
        Fetch and parse the b-file into a list of integers.

        Returns:
            list[int] or None: Parsed sequence values, or None on failure.
        """
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            return None

        data = []
        for line in response.text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                # format: n a(n)
                _, value = line.split()
                data.append(int(value))
            except (ValueError, IndexError):
                return None

        return data

    def get_filename(self):
        """
        Return the local filename of the OEIS b-file.

        Returns:
            str: The b-file filename (e.g., 'bA000045.txt').
        """
        return self.filename

    def get_url(self):
        """
        Return the URL of the OEIS b-file.

        Returns:
            str: The full URL pointing to the b-file on oeis.org.
        """
        return self.url

    def get_bfile_data(self):
        """
        Return the numeric data parsed from the OEIS b-file.

        Returns:
            list[int] or None: A list of sequence values extracted from the
            b-file, or None if the b-file could not be fetched or parsed.
        """
        return self.data

    def plot_data(self, show=True, ax=None, **plot_kwargs):
        """
        Plot parsed b-file values against their index.

        Args:
            show (bool): Call ``matplotlib.pyplot.show()`` when True.
            ax: Optional matplotlib Axes object to plot into.
            **plot_kwargs: Keyword arguments forwarded to ``ax.plot``.

        Returns:
            matplotlib.axes.Axes: The axes containing the plot.

        Raises:
            ValueError: If no b-file data is available.
            ImportError: If ``matplotlib`` is not installed.
        """
        values = self.get_bfile_data()
        if not values:
            raise ValueError("No b-file data available to plot.")

        try:
            import matplotlib.pyplot as plt
        except ImportError as exc:
            raise ImportError(
                "matplotlib is required for plotting. Install with: pip install matplotlib"
            ) from exc

        if ax is None:
            _, ax = plt.subplots()

        x_values = range(len(values))
        ax.plot(x_values, values, **plot_kwargs)
        ax.set_title(f"{self.oeis_id} b-file data")
        ax.set_xlabel("Index")
        ax.set_ylabel("Value")

        if show:
            plt.show()

        return ax
