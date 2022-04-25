from pathlib import Path

import pytest

from sphinxlint import main

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.mark.parametrize("file", [str(f) for f in (FIXTURE_DIR / "xpass").iterdir()])
def test_sphinxlint_shall_pass(file, capsys):
    try:
        main(["sphinxlint.py", str(file)])
    except SystemExit as err:
        error_count = err.code
    out, err = capsys.readouterr()
    assert out == "No problems found.\n"
    assert err == ""
    assert error_count == 0


@pytest.mark.parametrize(
    "file", [str(f) for f in (FIXTURE_DIR / "triggers-false-positive").iterdir()]
)
def test_sphinxlint_shall_trigger_false_positive(file, capsys):
    try:
        main(["sphinxlint.py", str(file)])
    except SystemExit as err:
        error_count = err.code
    out, err = capsys.readouterr()
    assert out == "No problems found.\n"
    assert err == ""
    assert error_count == 0
    try:
        main(["sphinxlint.py", "-f", str(file)])
    except SystemExit as err:
        error_count = err.code
    out, err = capsys.readouterr()
    assert out != "No problems found.\n"
    assert err == ""
    assert error_count > 0


@pytest.mark.parametrize("file", [str(f) for f in (FIXTURE_DIR / "xfail").iterdir()])
def test_sphinxlint_shall_not_pass(file, capsys):
    try:
        main(["sphinxlint.py", "--severity=0", str(file)])
    except SystemExit as err:
        error_count = err.code
    out, err = capsys.readouterr()
    assert out != "No problems found.\n"
    assert err == ""
    assert error_count > 0
