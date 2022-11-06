"""Sphinx linter."""

__version__ = "0.6.7"

from sphinxlint.sphinxlint import check_file, check_text

__all__ = ["check_text", "check_file"]
