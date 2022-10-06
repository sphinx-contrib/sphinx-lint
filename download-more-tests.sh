#!/bin/sh

# Repos known to pass:

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
