from pathlib import Path

import sphinxlint

import pytest

from sphinxlint import main

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.mark.parametrize("file", [str(f) for f in (FIXTURE_DIR / "xpass").iterdir()])
def test_sphinxlint_shall_pass(file, capsys):
    error_count = main(["sphinxlint.py", "--enable", "all", str(file)])
    out, err = capsys.readouterr()
    assert err == ""
    assert out == "No problems found.\n"
    assert error_count == 0


@pytest.mark.parametrize(
    "file", [str(f) for f in (FIXTURE_DIR / "triggers-false-positive").iterdir()]
)
def test_sphinxlint_shall_trigger_false_positive(file, capsys):
    error_count = main(["sphinxlint.py", str(file)])
    out, err = capsys.readouterr()
    assert out == "No problems found.\n"
    assert err == ""
    assert error_count == 0
    error_count = main(["sphinxlint.py", "--enable", "all", str(file)])
    out, err = capsys.readouterr()
    assert err == ""
    assert out != "No problems found.\n"
    assert error_count > 0


@pytest.mark.parametrize("file", [str(f) for f in (FIXTURE_DIR / "xfail").iterdir()])
def test_sphinxlint_shall_not_pass(file, capsys):
    error_count = main(["sphinxlint.py", "--enable", "all", str(file)])
    out, err = capsys.readouterr()
    assert out != "No problems found.\n"
    assert err == ""
    assert error_count > 0


@pytest.mark.parametrize("file", [str(FIXTURE_DIR / "paragraphs.rst")])
def test_paragraphs(file):
    with open(file) as f:
        lines = f.readlines()
    actual = sphinxlint.paragraphs(lines)
    for lno, para in actual:
        firstpline = para.splitlines(keepends=True)[0]
        # check that the first line of the paragraph matches the
        # corresponding line in the original file -- note that
        # `lines` is 0-indexed but paragraphs return 1-indexed values
        assert firstpline == lines[lno - 1]


@pytest.mark.parametrize("file", [str(FIXTURE_DIR / "paragraphs.rst")])
def test_line_no_in_error_msg(file, capsys):
    error_count = main(["sphinxlint.py", file])
    out, err = capsys.readouterr()
    assert err == ""
    assert "paragraphs.rst:76: role missing colon before" in out
    assert "paragraphs.rst:70: role use a single backtick" in out
    assert "paragraphs.rst:65: inline literal missing (escaped) space" in out
    assert error_count > 0
