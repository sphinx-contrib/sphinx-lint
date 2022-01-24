# Sphinx Lint

This is just [rstlint.py from
cpython](https://github.com/python/cpython/blob/main/Doc/tools/rstlint.py)
that I work here for ease.


## Known issues

`tokens = line.split("``")` cannot work, example of valid rst that
will break this detector:

    `it ``doesnt\`\` work`

because the double backticks starts a literal in a default role, but
the double backslash-backtick will close it without closing the
default role while being undetected by split.


## License

As this script was in the cpython repository the license is the PYTHON
SOFTWARE FOUNDATION LICENSE VERSION 2, see LICENSE file for a full
version.
