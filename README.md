# Sphinx Lint

Sphinx Lint is based on [rstlint.py from
cpython](https://github.com/python/cpython/blob/e0433c1e7/Doc/tools/rstlint.py).


## What sphinx-lint is, what it is not?

`sphinx-lint` should:

- be reasonably fast so it's comfortable to use as a linter in your editor.
- be usable on a single file.
- not give any false positive (probably an utopy, but let's try).
- not spend too much efforts finding errors that sphinx-build already find (or can easily find).
- focus on finding errors that are **not** visible to sphinx-build.


## Known issues

Currently sphinx-lint can't work with tables, there's no understanding
of how linesplit work in tables, like:

```rst
   +-----------------------------------------+-----------------------------+---------------+
   | Method                                  | Checks that                 | New in        |
   +=========================================+=============================+===============+
   | :meth:`assertEqual(a, b)                | ``a == b``                  |               |
   | <TestCase.assertEqual>`                 |                             |               |
   +-----------------------------------------+-----------------------------+---------------+
```

as sphinx-lint works line by line it will inevitably think the :meth: role is not closed properly.

To avoid false positives, some rules are skipped if we're in a table.


## License

As this script was in the cpython repository the license is the PYTHON
SOFTWARE FOUNDATION LICENSE VERSION 2, see LICENSE file for a full
version.
