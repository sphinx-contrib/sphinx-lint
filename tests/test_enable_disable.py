from random import choice
import re

from sphinxlint.__main__ import main

CHECKER_LINE = re.compile(r"^\s*- ([^:]+):", flags=re.MULTILINE)


def parse_checkers(text):
    """Given a --list output, returns a list of checkers names."""
    return CHECKER_LINE.findall(text)


def count_checkers(text):
    return len(parse_checkers(text))


def random_checker(text):
    return choice(parse_checkers(text))


def test_default(capsys):
    """Ensure that the output of `--list` includes at least 10 checkers."""
    main(["sphinxlint", "--list"])
    out, _err = capsys.readouterr()
    assert count_checkers(out) > 10


def test_disable_all(capsys):
    """Checks that disabling all checks actually disables them all."""
    main(["sphinxlint", "--disable", "all", "--list"])
    out, _err = capsys.readouterr()
    assert out == "No checkers selected.\n"


def test_enable_all(capsys):
    """Some checks are disabled by default, so enabling them all should
    give more checks than the default list."""
    main(["sphinxlint", "--list"])
    default_out, _err = capsys.readouterr()
    main(["sphinxlint", "--enable", "all", "--list"])
    all_out, _err = capsys.readouterr()
    assert count_checkers(default_out) < count_checkers(all_out)


def test_disable_one(capsys):
    """Disabling a single check from the default set (any of them) should
    give one check less than the default set."""
    main(["sphinxlint", "--list"])
    default_out, _err = capsys.readouterr()
    one_to_disable = random_checker(default_out)
    main(["sphinxlint", "--list", "--disable", one_to_disable])
    disabled_out, _err = capsys.readouterr()
    assert count_checkers(default_out) - 1 == count_checkers(disabled_out)


def test_enable_one(capsys):
    """Enabling a single check not enabled by default should give one
    check more than the default set."""
    main(["sphinxlint", "--list"])
    default_out, _err = capsys.readouterr()
    main(["sphinxlint", "--list", "--enable", "all"])
    all_out, _err = capsys.readouterr()
    not_enabled_by_default = list(
        set(parse_checkers(all_out)) - set(parse_checkers(default_out))
    )
    one_to_enable = choice(not_enabled_by_default)
    main(["sphinxlint", "--list", "--enable", one_to_enable])
    enabled_out, _err = capsys.readouterr()
    assert count_checkers(default_out) + 1 == count_checkers(enabled_out)
