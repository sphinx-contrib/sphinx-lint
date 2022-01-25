# Sphinx Lint

This is just [rstlint.py from
cpython](https://github.com/python/cpython/blob/main/Doc/tools/rstlint.py)
that I work here for ease.


## Known issues

Currently rstlint can't work with tables, there's no understanding of how linesplit work in tables, like:

```rst
   +-----------------------------------------+-----------------------------+---------------+
   | Method                                  | Checks that                 | New in        |
   +=========================================+=============================+===============+
   | :meth:`assertEqual(a, b)                | ``a == b``                  |               |
   | <TestCase.assertEqual>`                 |                             |               |
   +-----------------------------------------+-----------------------------+---------------+
```

as rstlint works line by line it will inevitably think the :meth: role is not closed properly.

To avoid false positives, some rules are skipped if we're in a table.


## License

As this script was in the cpython repository the license is the PYTHON
SOFTWARE FOUNDATION LICENSE VERSION 2, see LICENSE file for a full
version.
