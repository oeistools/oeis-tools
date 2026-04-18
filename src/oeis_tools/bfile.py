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

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

import requests

from .utils import oeis_bfile, oeis_url


def create_bfile(
    oeis_id: str, data: list[int], offset: int = 1, output_path: str | None = None
) -> str:
    """
    Create a b-file text file for a given OEIS sequence from a list of values.

    A b-file contains values of an integer sequence in the form:
    n a(n), one pair per line.

    Args:
        oeis_id (str): The OEIS identifier (e.g., 'A213676').
        data (list[int]): Sequence values to write to the b-file.
        offset (int): The starting index (n) for the sequence. Defaults to 1.
        output_path (str, optional): The directory or exact file path to save
            the b-file. If None, it saves to the current working directory
            using the standard b-file name (e.g., 'b213676.txt').

    Returns:
        str: The path to the created b-file.
    """
    filename = oeis_bfile(oeis_id)
    if output_path is None:
        file_path = Path(filename)
    else:
        path = Path(output_path)
        if path.is_dir():
            file_path = path / filename
        else:
            file_path = path

    with open(file_path, "w", encoding="utf-8") as f:
        for i, value in enumerate(data):
            f.write(f"{offset + i} {value}\n")

    return str(file_path)


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

    def __init__(self, oeis_id: str) -> None:
        self.oeis_id = oeis_id
        self.filename = oeis_bfile(oeis_id)
        self.url = oeis_url(oeis_id, fmt="bfile")
        self.indices = None
        self.data = self.fetch_bfile_data()

    def fetch_bfile_data(self) -> list[int] | None:
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

    def get_filename(self) -> str:
        """
        Return the local filename of the OEIS b-file.

        Returns:
            str: The b-file filename (e.g., 'bA000045.txt').
        """
        return self.filename

    def get_url(self) -> str:
        """
        Return the URL of the OEIS b-file.

        Returns:
            str: The full URL pointing to the b-file on oeis.org.
        """
        return self.url

    def get_bfile_data(self) -> list[int] | None:
        """
        Return the numeric data parsed from the OEIS b-file.

        Returns:
            list[int] or None: A list of sequence values extracted from the
            b-file, or None if the b-file could not be fetched or parsed.
        """
        return self.data

    def get_bfile_indices(self) -> list[int] | None:
        """
        Return index values parsed from the OEIS b-file first column.

        Returns:
            list[int] or None: A list of b-file indices, or None when parsing failed.
        """
        return self.indices

    def plot_data(
        self,
        n: int | None = None,
        show: bool = True,
        ax: Any = None,
        return_ax: bool = False,
        plot_style: str = "line",
        **plot_kwargs: Any,
    ) -> Any | None:
        """
        Plot parsed b-file values against their index.

        Args:
            n (int | None): Number of leading data points to plot. When ``None``,
                all available points are plotted.
            show (bool): Call ``matplotlib.pyplot.show()`` when True.
            ax: Optional matplotlib Axes object to plot into.
            return_ax (bool): Return the matplotlib Axes when True. Defaults to
                False to avoid notebook output noise.
            plot_style (str): Plot style for the data. Supported values:
                ``"line"`` (default), ``"joined"``, or ``"scatter"``.
            **plot_kwargs: Keyword arguments forwarded to ``ax.plot`` or
                ``ax.scatter`` depending on ``plot_style``.

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

        if not isinstance(plot_style, str):
            raise TypeError("plot_style must be a string.")

        plot_style_normalized = plot_style.strip().lower()
        if plot_style_normalized == "joined":
            plot_style_normalized = "line"

        if plot_style_normalized not in {"line", "scatter"}:
            raise ValueError(
                "plot_style must be one of: 'line', 'joined', or 'scatter'."
            )

        try:
            import matplotlib.pyplot as plt  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError(
                "matplotlib is required for plotting. "
                "Install with: pip install matplotlib"
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

        use_log_magnitude = any(
            abs(value) > sys.float_info.max for value in plot_values
        )

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
                else (
                    -safe_log10_abs_int(value)
                    if value < 0
                    else safe_log10_abs_int(value)
                )
                for value in plot_values
            ]
            if plot_style_normalized == "scatter":
                ax.scatter(x_values, y_values, **plot_kwargs)
            else:
                ax.plot(x_values, y_values, **plot_kwargs)
            title_suffix = " b-file data (log10 magnitude)"
            ax.set_ylabel("sign(value) * log10(|value|)")
        else:
            if plot_style_normalized == "scatter":
                ax.scatter(x_values, plot_values, **plot_kwargs)
            else:
                ax.plot(x_values, plot_values, **plot_kwargs)
            title_suffix = " b-file data"
            ax.set_ylabel(f"{self.oeis_id}(n)")

        ax.set_xlabel("n" if use_bfile_indices else "Index")
        current_title = ""
        if hasattr(ax, "get_title"):
            try:
                current_title = ax.get_title() or ""
            except TypeError:
                current_title = ""
        if (
            current_title
            and self.oeis_id not in current_title
            and current_title.endswith(title_suffix)
        ):
            combined = current_title.replace(
                title_suffix, f" + {self.oeis_id}{title_suffix}"
            )
            ax.set_title(combined)
        else:
            ax.set_title(f"{self.oeis_id}{title_suffix}")

        if show:
            plt.show()

        return ax if return_ax else None
