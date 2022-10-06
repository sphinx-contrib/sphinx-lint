#!/bin/sh

# Helper script to generate more tests using repos from friends.
#
# Once downloaded they can be tested using pytest:
#
#    python -m pytest
#
# It's possible to filter by project name like:
#
#    python -m pytest -k devguide


# Repos known to pass are listed below in the following format:
#
#     URL DOC_FOLDER SPHINXLINT_FLAGS...
#
# (If the doc is at the root of the repo: use a dot as a folder name.)

# Yes the following comment **is** the list of repos to download, you
# can edit it.

# https://github.com/jazzband/django-oauth-toolkit docs
# https://github.com/neo4j/neo4j-python-driver docs
# https://github.com/pandas-dev/pandas doc
# https://github.com/python/cpython Doc --enable default-role
# https://github.com/python/devguide/ . --enable default-role
# https://github.com/spyder-ide/spyder-docs doc --enable all --disable line-too-long
# https://github.com/sympy/sympy doc
# https://github.com/sphinx-doc/sphinx doc --enable line-too-long --max-line-length 85

grep '^# https://' "$0" |
    while read -r _ repo directory flags
    do
        name="$(basename "$repo")"
        if ! [ -d "tests/fixtures/friends/$name" ]
        then
            if [ "$directory" != "." ]
            then
                git clone --depth 1 --sparse --filter=blob:none "$repo" "tests/fixtures/friends/$name" &&
                    (
                        cd "tests/fixtures/friends/$name" || exit
                        rm *  # Removes files at root of repo (READMEs, conftest.py, ...)
                        git sparse-checkout init --cone
                        git sparse-checkout set "$directory"
                    )
            else
                git clone --depth 1 "$repo" "tests/fixtures/friends/$name"
            fi
        fi
        printf "%s\n" "$flags" > "tests/fixtures/friends/$name/flags"
    done

# Remove exceptions:

rm -f tests/fixtures/friends/cpython/Doc/README.rst
