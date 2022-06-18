#!/bin/sh

# Repos known to pass:

# https://github.com/jazzband/django-oauth-toolkit docs
# https://github.com/neo4j/neo4j-python-driver docs
# https://github.com/pandas-dev/pandas doc
# https://github.com/python/cpython Doc
# https://github.com/spyder-ide/spyder-docs doc
# https://github.com/sympy/sympy doc
# https://github.com/sphinx-doc/sphinx doc

grep '^# https://' "$0" |
    while read -r _ repo directory
    do
        name="$(basename "$repo")"
        if ! [ -d "tests/fixtures/xpass/$name" ]
        then
            git clone --depth 1 --sparse --filter=blob:none "$repo" "tests/fixtures/xpass/$name" &&
            (
                cd "tests/fixtures/xpass/$name" || exit
                rm *  # Removes files at root of repo (READMEs, conftest.py, ...)
                git sparse-checkout init --cone
                git sparse-checkout set "$directory"
            )
        fi
    done

# Remove exceptions:

rm -f tests/fixtures/xpass/cpython/Doc/README.rst
