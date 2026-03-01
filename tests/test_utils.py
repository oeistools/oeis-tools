# SPDX-License-Identifier: MIT
# Copyright (c) 2025 EnriquePH

"""Tests for utility helpers in ``oeis_tools.utils``."""

import pytest

from oeis_tools.utils import (
    OEIS_URL,
    check_id,
    oeis_bfile,
    oeis_keyword_description,
    oeis_url,
)


def test_check_id_accepts_valid_oeis_id():
    """Accept IDs that match the OEIS pattern."""
    assert check_id("A000001") is True


def test_check_id_rejects_invalid_oeis_ids():
    """Reject IDs with wrong prefix or wrong length/characters."""
    assert check_id("A12345") is False
    assert check_id("B000001") is False
    assert check_id("A0000012") is False
    assert check_id("A12ABC") is False


def test_oeis_bfile_builds_expected_filename():
    """Build the expected OEIS b-file filename from a valid ID."""
    assert oeis_bfile("A000045") == "b000045.txt"


def test_oeis_bfile_raises_for_invalid_id():
    """Raise ``ValueError`` when b-file is requested for an invalid ID."""
    with pytest.raises(ValueError, match="Invalid OEIS ID"):
        oeis_bfile("A123")


def test_oeis_url_builds_supported_formats():
    """Generate valid OEIS URLs for default and known formats."""
    assert oeis_url("A000001") == f"{OEIS_URL}/A000001"
    assert oeis_url("A000001", fmt="json") == f"{OEIS_URL}/search?q=id:A000001&fmt=json"
    assert oeis_url("A000001", fmt="text") == f"{OEIS_URL}/search?q=id:A000001&fmt=text"
    assert oeis_url("A000001", fmt="bfile") == f"{OEIS_URL}/A000001/b000001.txt"
    assert oeis_url("A000001", fmt="graph") == f"{OEIS_URL}/A000001/graph?png=1"


def test_oeis_url_falls_back_to_default_for_unknown_format():
    """Use the default entry URL when an unknown format is provided."""
    assert oeis_url("A000001", fmt="unknown") == f"{OEIS_URL}/A000001"


def test_oeis_keyword_description_returns_expected_description():
    """Return wiki description text for a known OEIS keyword tag."""
    assert oeis_keyword_description("nonn") == (
        "Displayed terms are nonnegative (later terms may still become negative)."
    )


def test_oeis_keyword_description_normalizes_and_handles_unknown():
    """Normalize case/whitespace and return None for unknown tags."""
    assert oeis_keyword_description("  EASY  ") == (
        "It is easy to produce terms of this sequence."
    )
    assert oeis_keyword_description("not-a-tag") is None
    assert oeis_keyword_description("") is None
