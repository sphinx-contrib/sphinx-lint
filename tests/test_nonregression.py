import pytest
from rstlint import main


def test_role_missing_column(capsys, tmp_path):
    """rstlint should find missing leading column in roles."""
    file = tmp_path / "testfile.rst"
    file.write_text("The c:macro:`PY_VERSION_HEX` miss a column.\n", encoding="UTF-8")
    error_count = main(["rstlint.py", str(tmp_path)])
    out, err = capsys.readouterr()
    assert "column" in out
    assert not err
    assert error_count == 1


@pytest.mark.xfail(strict=True)
def test_last_line(capsys, tmp_path):
    """Check regression of last line ending with space, a char, and no newline.

    It wrongly raised a "trailing whitespace".
    """

    file = tmp_path / "testfile.rst"
    file.write_text("Hell o", encoding="UTF-8")
    main(["rstlint.py", str(tmp_path)])
    out, err = capsys.readouterr()
    assert not err
    assert "trailing whitespace" not in out
