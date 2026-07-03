import re

from sphinxlint.cli import main

CHECKER_LINE = re.compile(r"^\s*- ([^:]+):", flags=re.MULTILINE)
CHECKER_SECTION = re.compile(
    r"^(?:\d+|No) (?P<status>enabled|disabled) checkers[:.]\n"
    r"(?P<body>.*?)"
    r"(?=^(?:\d+|No) (?:enabled|disabled) checkers[:.]|\Z)",
    flags=re.MULTILINE | re.DOTALL,
)


def parse_checkers(text, status):
    """Return checker names from an enabled or disabled --list section."""
    sections = {
        match["status"]: CHECKER_LINE.findall(match["body"])
        for match in CHECKER_SECTION.finditer(text)
    }
    return sections[status]


def enabled_checkers(text):
    return parse_checkers(text, "enabled")


def disabled_checkers(text):
    return parse_checkers(text, "disabled")


def test_default(capsys):
    """Ensure that `--list` shows enabled and disabled checkers."""
    main(["sphinxlint", "--list"])
    out, _err = capsys.readouterr()
    assert len(enabled_checkers(out)) > 10
    assert "default-role" in disabled_checkers(out)


def test_disable_all(capsys):
    """Checks that disabling all checks actually disables them all."""
    main(["sphinxlint", "--disable", "all", "--list"])
    out, _err = capsys.readouterr()
    assert enabled_checkers(out) == []
    assert disabled_checkers(out)


def test_enable_all(capsys):
    """Enabling all checks moves all checkers into the enabled section."""
    main(["sphinxlint", "--list"])
    default_out, _err = capsys.readouterr()
    main(["sphinxlint", "--enable", "all", "--list"])
    all_out, _err = capsys.readouterr()
    assert set(enabled_checkers(default_out)) | set(
        disabled_checkers(default_out)
    ) == set(enabled_checkers(all_out))
    assert disabled_checkers(all_out) == []


def test_disable_one(capsys):
    """Disabling one default check moves it into the disabled section."""
    main(["sphinxlint", "--list"])
    default_out, _err = capsys.readouterr()
    one_to_disable = enabled_checkers(default_out)[0]
    main(["sphinxlint", "--list", "--disable", one_to_disable])
    disabled_out, _err = capsys.readouterr()
    assert set(enabled_checkers(default_out)) - {one_to_disable} == set(
        enabled_checkers(disabled_out)
    )
    assert set(disabled_checkers(default_out)) | {one_to_disable} == set(
        disabled_checkers(disabled_out)
    )


def test_enable_one(capsys):
    """Enabling one opt-in check moves it into the enabled section."""
    main(["sphinxlint", "--list"])
    default_out, _err = capsys.readouterr()
    one_to_enable = disabled_checkers(default_out)[0]
    main(["sphinxlint", "--list", "--enable", one_to_enable])
    enabled_out, _err = capsys.readouterr()
    assert set(enabled_checkers(default_out)) | {one_to_enable} == set(
        enabled_checkers(enabled_out)
    )
    assert set(disabled_checkers(default_out)) - {one_to_enable} == set(
        disabled_checkers(enabled_out)
    )
