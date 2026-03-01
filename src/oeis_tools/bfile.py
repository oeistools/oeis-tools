# SPDX-License-Identifier: MIT
# Copyright (c) 2025 EnriquePH

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

import math
import sys

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
        self.indices = None
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

        indices = []
        data = []
        for line in response.text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                # format: n a(n)
                index, value, *_ = line.split()
                indices.append(int(index))
                data.append(int(value))
            except (ValueError, IndexError):
                self.indices = None
                return None

        self.indices = indices
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

    def get_bfile_indices(self):
        """
        Return index values parsed from the OEIS b-file first column.

        Returns:
            list[int] or None: A list of b-file indices, or None when parsing failed.
        """
        return self.indices

    def plot_data(self, n=None, show=True, ax=None, return_ax=False, **plot_kwargs):
        """
        Plot parsed b-file values against their index.

        Args:
            n (int | None): Number of leading data points to plot. When ``None``,
                all available points are plotted.
            show (bool): Call ``matplotlib.pyplot.show()`` when True.
            ax: Optional matplotlib Axes object to plot into.
            return_ax (bool): Return the matplotlib Axes when True. Defaults to
                False to avoid notebook output noise.
            **plot_kwargs: Keyword arguments forwarded to ``ax.plot``.

        Returns:
            matplotlib.axes.Axes | None: The axes when ``return_ax=True``;
            otherwise ``None``.

        Raises:
            ValueError: If no b-file data is available.
            ImportError: If ``matplotlib`` is not installed.
        """
        values = self.get_bfile_data()
        if not values:
            raise ValueError("No b-file data available to plot.")

        if n is not None:
            if not isinstance(n, int):
                raise TypeError("n must be an integer or None.")
            if n < 0:
                raise ValueError("n must be non-negative.")

        try:
            import matplotlib.pyplot as plt  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError(
                "matplotlib is required for plotting. Install with: pip install matplotlib"
            ) from exc

        if ax is None:
            _, ax = plt.subplots()

        indices = self.get_bfile_indices()
        plot_values = values if n is None else values[:n]
        use_bfile_indices = bool(indices) and len(indices) == len(values)
        if use_bfile_indices:
            x_values = indices if n is None else indices[:n]
        else:
            x_values = range(len(plot_values))

        use_log_magnitude = any(abs(value) > sys.float_info.max for value in plot_values)

        if use_log_magnitude:
            # Matplotlib stores data as float; extremely large integers overflow.
            log10_2 = math.log10(2.0)

            def safe_log10_abs_int(value):
                absolute = abs(value)
                if absolute <= sys.float_info.max:
                    return math.log10(absolute)

                # Compute log10(n) using bit-length scaling to avoid float overflow.
                shift = max(absolute.bit_length() - 53, 0)
                mantissa = absolute >> shift
                return math.log10(mantissa) + shift * log10_2

            y_values = [
                0.0
                if value == 0
                else (-safe_log10_abs_int(value) if value < 0 else safe_log10_abs_int(value))
                for value in plot_values
            ]
            ax.plot(x_values, y_values, **plot_kwargs)
            ax.set_title(f"{self.oeis_id} b-file data (log10 magnitude)")
            ax.set_ylabel("sign(value) * log10(|value|)")
        else:
            ax.plot(x_values, plot_values, **plot_kwargs)
            ax.set_title(f"{self.oeis_id} b-file data")
            ax.set_ylabel("Value")

        ax.set_xlabel("n" if use_bfile_indices else "Index")

        if show:
            plt.show()

        return ax if return_ax else None
