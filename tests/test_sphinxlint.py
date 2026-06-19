import re
from pathlib import Path

import pytest

from sphinxlint.cli import main
from sphinxlint.utils import paragraphs

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.mark.parametrize("file", [str(f) for f in (FIXTURE_DIR / "xpass").iterdir()])
def test_sphinxlint_shall_pass(file, capsys):
    has_errors = main(["sphinxlint.py", "--enable", "all", str(file)])
    out, err = capsys.readouterr()
    assert err == ""
    assert out == "No problems found.\n"
    assert not has_errors


@pytest.mark.parametrize(
    "file", [str(f) for f in (FIXTURE_DIR / "triggers-false-positive").iterdir()]
)
def test_sphinxlint_shall_trigger_false_positive(file, capsys):
    has_errors = main(["sphinxlint.py", str(file)])
    out, err = capsys.readouterr()
    assert out == "No problems found.\n"
    assert err == ""
    assert not has_errors
    has_errors = main(["sphinxlint.py", "--enable", "all", str(file)])
    out, err = capsys.readouterr()
    assert out != "No problems found.\n"
    assert err != ""
    assert has_errors


def test_sphinxlint_output(fixture_dir, capsys):
    """This test is here to spot unwanted changes in the display of errors."""
    result = main(["sphinxlint.py", str(fixture_dir / "hierarchy" / "outer.rst")])
    assert result == 1
    out, err = capsys.readouterr()
    assert (
        "hierarchy/outer.rst:5: "
        "role missing opening tag colon ( attr:`). (missing-space-before-role)\n" in err
    )
    assert not out


def test_sphinxlint_cannot_read_file(tmp_path, capsys):
    file = tmp_path / "file.rst"
    file.touch()
    file.chmod(0)
    result = main(["sphinxlint.py", str(file)])
    assert result == 1
    out, err = capsys.readouterr()
    assert re.match(
        r".*file.rst:0: cannot open: \[Errno 13\] Permission denied: "
        r"'.*file.rst' \(check_file\)",
        err,
    )
    assert not out


def gather_xfail():
    """Find all rst files in the fixtures/xfail directory.

    Each file is searched for lines containing expcted errors, they
    are starting with `.. expect: `.
    """
    marker = ".. expect: "
    for file in (FIXTURE_DIR / "xfail").iterdir():
        expected_errors = []
        for line in Path(file).read_text(encoding="UTF-8").splitlines():
            if line.startswith(marker):
                expected_errors.append(line[len(marker) :])
        yield str(file), expected_errors


@pytest.mark.parametrize("file,expected_errors", gather_xfail())
def test_sphinxlint_shall_not_pass(file, expected_errors, capsys):
    has_errors = main(["sphinxlint.py", "--enable", "all", file])
    out, err = capsys.readouterr()
    assert out != "No problems found.\n"
    assert err != ""
    assert has_errors
    assert expected_errors, (
        "That's not OK not to tell which errors are expected, "
        """add one using a ".. expect: " line."""
    )
    for expected_error in expected_errors:
        assert expected_error in err
    number_of_expected_errors = len(expected_errors)
    number_of_reported_errors = len(err.splitlines())
    assert number_of_expected_errors == number_of_reported_errors, (
        f"{number_of_reported_errors=}, {err=}"
    )


@pytest.mark.parametrize("file", [str(FIXTURE_DIR / "paragraphs.rst")])
def test_paragraphs(file):
    with open(file) as f:
        lines = tuple(f.readlines())
    actual = paragraphs(lines)
    for lno, para in actual:
        firstpline = para.splitlines(keepends=True)[0]
        # check that the first line of the paragraph matches the
        # corresponding line in the original file -- note that
        # `lines` is 0-indexed but paragraphs return 1-indexed values
        assert firstpline == lines[lno - 1]


@pytest.mark.parametrize("file", [str(FIXTURE_DIR / "paragraphs.rst")])
def test_line_no_in_error_msg(file, capsys):
    has_errors = main(["sphinxlint.py", file])
    out, err = capsys.readouterr()
    assert out == ""
    assert err.count("paragraphs.rst:76: role missing colon before") == 2
    assert "paragraphs.rst:70: role use a single backtick" in err
    assert "paragraphs.rst:65: inline literal missing (escaped) space" in err
    assert has_errors
