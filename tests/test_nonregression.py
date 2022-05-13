import pytest

from sphinxlint import check_text, checkers


@pytest.fixture
def check_str(capsys):
    def _check_str(rst):
        error_count = check_text("test.rst", rst, checkers.values())
        out, err = capsys.readouterr()
        assert not err
        return error_count, out

    yield _check_str


def test_role_missing_colon(check_str):
    """sphinx-lint should find missing leading colon in roles.

    It's at the end the same as role glued with word.
    """
    error_count, out = check_str("The c:macro:`PY_VERSION_HEX` miss a colon.\n")
    assert "role" in out
    assert error_count


def test_last_line(check_str):
    """Check regression of last line ending with space, a char, and no newline.

    It wrongly raised a "trailing whitespace".
    """
    _, out = check_str("Hell o")
    assert "trailing whitespace" not in out


def test_last_line_has_no_newline(check_str):
    error_count, out = check_str("Hello\nworld")
    assert "No newline at end of file" in out
    assert error_count


def test_inline_literal_inside_role(check_str):
    error_count, out = check_str(
        r""":emphasis:`This ``Too Shall\`\` Pass`
even ``followed`` by ``inline literals``.
""",
    )
    assert not out
    assert not error_count


def test_roles_may_not_be_hardcoded(check_str):
    error_count, out = check_str("such as :std:doc:`PyPA build <pypa-build:index>`\n")
    assert not out
    assert not error_count
