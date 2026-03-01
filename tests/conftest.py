# SPDX-License-Identifier: MIT
# Copyright (c) 2025 EnriquePH

"""Pytest configuration for local source imports."""

import pathlib
import sys


SRC_DIR = pathlib.Path(__file__).resolve().parents[1] / "src"
src_path = str(SRC_DIR)
if src_path not in sys.path:
    sys.path.insert(0, src_path)
