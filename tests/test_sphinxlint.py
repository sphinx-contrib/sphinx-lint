import re
from pathlib import Path

import pytest
from sphinxlint.cli import main
from sphinxlint.utils import paragraphs

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.mark.parametrize("file", [str(f) for f in (FIXTURE_DIR / "xpass").iterdir()])
def test_sphinxlint_shall_pass(file, capsys):
    has_errors = main(
        ["sphinxlint.py", "--check-docstrings", "--enable", "all", str(file)]
    )
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
    has_errors = main(
        ["sphinxlint.py", "--check-docstrings", "--enable", "all", str(file)]
    )
    out, err = capsys.readouterr()
    assert out != "No problems found.\n"
    assert err != ""
    assert has_errors


def gather_xfail():
    """Find all rst files in the fixtures/xfail directory.

    Each file is searched for lines containing expcted errors, they
    are starting with `.. expect: `.
    """
    marker = re.compile(r"(\.\.|#) expect: ")
    for file in (FIXTURE_DIR / "xfail").iterdir():
        expected_errors = []
        for line in Path(file).read_text(encoding="UTF-8").splitlines():
            if match := marker.match(line):
                expected_errors.append(line[len(match[0]) :])
        yield str(file), expected_errors


@pytest.mark.parametrize("file,expected_errors", gather_xfail())
def test_sphinxlint_shall_not_pass(file, expected_errors, capsys):
    has_errors = main(["sphinxlint.py", "--check-docstrings", "--enable", "all", file])
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
    assert (
        number_of_expected_errors == number_of_reported_errors
    ), f"{number_of_reported_errors=}, {err=}"


def test_check_docstrings_flag(subtests):
    for file in (FIXTURE_DIR / "xfail").glob("*.py"):
        with subtests.test(msg="with file", file=file):
            with subtests.test(msg="With --check-docstrings"):
                has_errors = main(
                    [
                        "sphinxlint.py",
                        "--check-docstrings",
                        "--enable",
                        "all",
                        str(file),
                    ]
                )
                assert has_errors
            with subtests.test(msg="Without --check-docstrings"):
                has_errors = main(["sphinxlint.py", "--enable", "all", str(file)])
                assert not has_errors


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
