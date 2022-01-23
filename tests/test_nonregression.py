import pytest
from rstlint import check


def test_role_missing_column(capsys):
    """rstlint should find missing leading column in roles."""
    error_count = check("test.rst", "The c:macro:`PY_VERSION_HEX` miss a column.\n")
    out, err = capsys.readouterr()
    assert "column" in out
    assert not err
    assert error_count


def test_last_line(capsys):
    """Check regression of last line ending with space, a char, and no newline.

    It wrongly raised a "trailing whitespace".
    """
    check("test.rst", "Hell o")
    out, err = capsys.readouterr()
    assert not err
    assert "trailing whitespace" not in out
