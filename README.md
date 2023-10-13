# Sphinx Lint

[![PyPI](https://img.shields.io/pypi/v/sphinx-lint)
 ![Monthly downloads](https://img.shields.io/pypi/dm/sphinx-lint)
 ![Supported Python Version](https://img.shields.io/pypi/pyversions/sphinx-lint.svg)
](https://pypi.org/project/sphinx-lint)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/sphinx-contrib/sphinx-lint/tests.yml?branch=main)](https://github.com/sphinx-contrib/sphinx-lint/actions)

Sphinx Lint is based on [rstlint.py from
CPython](https://github.com/python/cpython/blob/e0433c1e7/Doc/tools/rstlint.py).


## What is Sphinx Lint, what is it not?

`sphinx-lint` should:

- be reasonably fast so it's comfortable to use as a linter in your editor.
- be usable on a single file.
- not give any false positives (probably a utopia, but let's try).
- not spend too much effort finding errors that sphinx-build already finds (or can easily find).
- focus on finding errors that are **not** visible to sphinx-build.


## Using Sphinx Lint

To use Sphinx Lint, run:

```console
$ sphinx-lint           # check all dirs and files
$ sphinx-lint file.rst  # check a single file
$ sphinx-lint docs      # check a directory
$ sphinx-lint -i venv   # ignore a file/directory
$ sphinx-lint -h        # for more options
```

Sphinx Lint can also be used via [pre-commit](https://pre-commit.com).
We recommend using a configuration like this:

```yaml
  - repo: https://github.com/sphinx-contrib/sphinx-lint
    rev: LATEST_SPHINXLINT_RELEASE_TAG
    hooks:
      - id: sphinx-lint
        args: [--jobs=1]
        types: [rst]
```

In particular, note that the `--jobs=1` flag is recommended for use with pre-commit.
By default, Sphinx Lint uses `multiprocessing` to lint multiple files simultaneously,
but this interacts poorly with pre-commit, which also attempts to use multiprocessing,
leading to resource contention. Adding `--jobs=1` tells Sphinx Lint not to use
multiprocessing itself, deferring to pre-commit on the best way to delegate resources
across available cores.


## Known issues

Currently Sphinx Lint can't work with tables, there's no understanding
of how `linesplit` works in tables, like:

```rst
   +-----------------------------------------+-----------------------------+---------------+
   | Method                                  | Checks that                 | New in        |
   +=========================================+=============================+===============+
   | :meth:`assertEqual(a, b)                | ``a == b``                  |               |
   | <TestCase.assertEqual>`                 |                             |               |
   +-----------------------------------------+-----------------------------+---------------+
```

as Sphinx Lint works line by line it will inevitably think the `:meth:` role is not closed properly.

To avoid false positives, some rules are skipped if we're in a table.


## Contributing

A quick way to test if some syntax is valid from a pure
reStructuredText point of view, one case use `docutils`'s `pseudoxml`
writer, like:

```text
$ docutils --writer=pseudoxml tests/fixtures/xpass/role-in-code-sample.rst
<document source="tests/fixtures/xpass/role-in-code-sample.rst">
    <paragraph>
        Found in the pandas documentation, this is valid:
    <bullet_list bullet="*">
        <list_item>
            <paragraph>
                A pandas class (in the form
                <literal>
                    :class:`pandas.Series`
                )
        <list_item>
            <paragraph>
                A pandas method (in the form
                <literal>
                    :meth:`pandas.Series.sum`
                )
        <list_item>
            <paragraph>
                A pandas function (in the form
                <literal>
                    :func:`pandas.to_datetime`
                )
    <paragraph>
        it's documenting roles using code samples (double backticks).
```


## Releasing

First test with friends projects by running:

    sh download-more-tests.sh
    python -m pytest

Bump the version in `sphinxlint.py`, commit, tag, push:

    git tag v0.6.5
    git push
    git push --tags

To release on PyPI run:

    python -m pip install --upgrade build twine
    python -m build
    python -m twine upload dist/*


## License

As this script was in the CPython repository the license is the Python
Software Foundation Licence Version 2, see the LICENSE file for a full
version.
