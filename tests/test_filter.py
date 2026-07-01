from sphinxlint.cli import main


def test_sphinxlint_ignore_by_filename(fixture_dir, capsys):
    main(["sphinxlint.py", "--ignore", "inner.rst", str(fixture_dir / "hierarchy")])
    out, err = capsys.readouterr()
    assert "outer.rst" in err
    assert "inner.rst" not in err


def test_sphinxlint_ignore_by_path(fixture_dir, capsys):
    main(["sphinxlint.py", "--ignore", "dir/inner.rst", str(fixture_dir / "hierarchy")])
    out, err = capsys.readouterr()
    assert "outer.rst" in err
    assert "inner.rst" not in err
