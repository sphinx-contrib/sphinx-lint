# Sphinx Lint

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


## License

As this script was in the CPython repository the license is the Python
Software Foundation Licence Version 2, see the LICENSE file for a full
version.
