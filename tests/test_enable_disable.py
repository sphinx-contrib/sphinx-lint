from random import choice

from sphinxlint import main

BULLET = "- "


def test_default(capsys):
    main(["sphinxlint", "--list"])
    out, _err = capsys.readouterr()
    assert out.count(BULLET) > 10


def test_disable_all(capsys):
    main(["sphinxlint", "--disable", "all", "--list"])
    out, _err = capsys.readouterr()
    assert out.count(BULLET) == 0


def test_enable_all(capsys):
    main(["sphinxlint", "--list"])
    default_out, _err = capsys.readouterr()
    main(["sphinxlint", "--enable", "all", "--list"])
    all_out, _err = capsys.readouterr()
    assert default_out.count(BULLET) < all_out.count(BULLET)


def test_disable_one(capsys):
    main(["sphinxlint", "--list"])
    default_out, _err = capsys.readouterr()
    one_to_disable = choice(default_out.splitlines())[2:].split(":")[0]
    main(["sphinxlint", "--list", "--disable", one_to_disable])
    disabled_out, _err = capsys.readouterr()
    assert default_out.count(BULLET) - 1 == disabled_out.count(BULLET)


def test_enable_one(capsys):
    main(["sphinxlint", "--list"])
    default_out, _err = capsys.readouterr()
    main(["sphinxlint", "--list", "--enable", "all"])
    all_out, _err = capsys.readouterr()
    not_enabled_by_default = set(all_out.splitlines()) - set(default_out.splitlines())
    one_to_enable = choice(list(not_enabled_by_default))[2:].split(":")[0]
    main(["sphinxlint", "--list", "--enable", one_to_enable])
    enabled_out, _err = capsys.readouterr()
    assert default_out.count(BULLET) + 1 == enabled_out.count(BULLET)
