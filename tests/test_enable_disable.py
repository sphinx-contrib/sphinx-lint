from random import choice
import re

from sphinxlint import main

BULLET = re.compile(r"^\s*- ", flags=re.MULTILINE)


def count_bullets(text):
    return len(BULLET.findall(text))


def test_default(capsys):
    main(["sphinxlint", "--list"])
    out, _err = capsys.readouterr()
    assert count_bullets(out) > 10


def test_disable_all(capsys):
    main(["sphinxlint", "--disable", "all", "--list"])
    out, _err = capsys.readouterr()
    assert count_bullets(out) == 0


def test_enable_all(capsys):
    main(["sphinxlint", "--list"])
    default_out, _err = capsys.readouterr()
    main(["sphinxlint", "--enable", "all", "--list"])
    all_out, _err = capsys.readouterr()
    assert count_bullets(default_out) < count_bullets(all_out)


def test_disable_one(capsys):
    main(["sphinxlint", "--list"])
    default_out, _err = capsys.readouterr()
    one_to_disable = choice(default_out.splitlines())[2:].split(":")[0]
    main(["sphinxlint", "--list", "--disable", one_to_disable])
    disabled_out, _err = capsys.readouterr()
    assert count_bullets(default_out) - 1 == count_bullets(disabled_out)


def test_enable_one(capsys):
    main(["sphinxlint", "--list"])
    default_out, _err = capsys.readouterr()
    main(["sphinxlint", "--list", "--enable", "all"])
    all_out, _err = capsys.readouterr()
    not_enabled_by_default = set(all_out.splitlines()) - set(default_out.splitlines())
    one_to_enable = choice(list(not_enabled_by_default))[2:].split(":")[0]
    main(["sphinxlint", "--list", "--enable", one_to_enable])
    enabled_out, _err = capsys.readouterr()
    assert count_bullets(default_out) + 1 == count_bullets(enabled_out)
