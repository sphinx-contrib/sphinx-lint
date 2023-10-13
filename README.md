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

1. Make sure that the [CI tests pass](https://github.com/sphinx-contrib/sphinx-lint/actions)
   and optionally double-check locally with friends projects by running:
   
       sh download-more-tests.sh
       python -m pytest
2. Go on the [Releases page](https://github.com/sphinx-contrib/sphinx-lint/releases)
3. Click "Draft a new release"
4. Click "Choose a tag"
5. Type the next vX.Y.Z version "Create new tag: vX.Y.Z on publish"
6. Leave the "Release title" blank (it will be autofilled)
7. Click "Generate release notes" and amend as required
8. Click "Publish release"
9. Check the tagged
   [GitHub Actions build](https://github.com/sphinx-contrib/sphinx-lint/actions/workflows/deploy.yml)
   has [deployed to PyPI](https://pypi.org/project/sphinx-lint/#history)


## License

As this script was in the CPython repository the license is the Python
Software Foundation Licence Version 2, see the LICENSE file for a full
version.
