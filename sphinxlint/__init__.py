"""Sphinx linter."""

import importlib.metadata

from sphinxlint.sphinxlint import check_file, check_text

__version__ = importlib.metadata.version("sphinx_lint")

__all__ = ["check_text", "check_file"]
