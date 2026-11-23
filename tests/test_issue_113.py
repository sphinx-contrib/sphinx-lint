"""Tests for issue #113: ``--ignore`` should accept a list of paths."""

import pytest

from sphinxlint.cli import main

FIXTURE = "trailing whitespace here \n"


@pytest.fixture
def tree(tmp_path):
    """Build a tree with two ignorable subdirs, each holding a faulty file."""
    for name in ("d1", "d2"):
        sub = tmp_path / name
        sub.mkdir()
        (sub / "faulty.rst").write_text(FIXTURE, encoding="UTF-8")
    return tmp_path


def test_ignore_comma_separated(tree, capsys):
    """``-i d1,d2`` must ignore both directories."""
    has_errors = main(["sphinxlint.py", "-i", "d1,d2", str(tree)])
    out, err = capsys.readouterr()
    assert err == ""
    assert out == "No problems found.\n"
    assert not has_errors


def test_ignore_repeated_option_still_works(tree, capsys):
    """Control: the historical ``-i a -i b`` form keeps working."""
    has_errors = main(["sphinxlint.py", "-i", "d1", "-i", "d2", str(tree)])
    out, err = capsys.readouterr()
    assert err == ""
    assert out == "No problems found.\n"
    assert not has_errors


def test_ignore_single_path_still_works(tree, capsys):
    """Control: a single ``-i`` still ignores exactly one directory."""
    has_errors = main(["sphinxlint.py", "-i", "d1", str(tree)])
    _out, err = capsys.readouterr()
    assert "d2" in err
    assert "d1" not in err
    assert has_errors


def test_empty_ignore_value_does_not_ignore_everything(tree, capsys):
    """An empty value must not silence the whole run."""
    has_errors = main(["sphinxlint.py", "-i", "", str(tree)])
    _out, err = capsys.readouterr()
    assert "d1" in err
    assert "d2" in err
    assert has_errors
