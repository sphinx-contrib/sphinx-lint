import pytest
from rstlint import main


@pytest.mark.xfail(strict=True)
def test_role_missing_column(capsys, tmp_path):
    """rstlint should find missing leading column in roles."""
    file = tmp_path / "testfile.rst"
    file.write_text("The c:macro:`PY_VERSION_HEX` miss a column.\n", encoding="UTF-8")
    error_count = main(["rstlint.py", str(tmp_path)])
    out, err = capsys.readouterr()
    assert "column" in out
    assert err == ""
    assert error_count == 1
