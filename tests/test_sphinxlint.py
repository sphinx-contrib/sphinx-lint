from pathlib import Path

import pytest

from sphinxlint import main

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.mark.parametrize("file", [str(f) for f in (FIXTURE_DIR / "xpass").glob("*.*")])
def test_sphinxlint_shall_pass(file, capsys):
    error_count = main(["sphinxlint.py", str(file)])
    out, err = capsys.readouterr()
    assert out == "No problems found.\n"
    assert err == ""
    assert error_count == 0


@pytest.mark.parametrize("file", [str(f) for f in (FIXTURE_DIR / "xfail").glob("*.*")])
def test_sphinxlint_shall_not_pass(file, capsys):
    error_count = main(["sphinxlint.py", str(file)])
    out, err = capsys.readouterr()
    assert out != "No problems found.\n"
    assert err == ""
    assert error_count > 0
