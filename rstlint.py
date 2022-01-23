#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Check for stylistic and formal issues in .rst and .py
# files included in the documentation.
#
# 01/2009, Georg Brandl

# TODO: - wrong versions in versionadded/changed
#       - wrong markup after versionchanged directive

"""Sphinx rst linter.
"""

import os
import re
import sys
import argparse
from string import ascii_letters
from os.path import join, splitext, exists, isfile
from collections import Counter

# fmt: off
directives = [
    # standard docutils ones
    'admonition', 'attention', 'caution', 'class', 'compound', 'container',
    'contents', 'csv-table', 'danger', 'date', 'default-role', 'epigraph',
    'error', 'figure', 'footer', 'header', 'highlights', 'hint', 'image',
    'important', 'include', 'line-block', 'list-table', 'meta', 'note',
    'parsed-literal', 'pull-quote', 'raw', 'replace',
    'restructuredtext-test-directive', 'role', 'rubric', 'sectnum', 'sidebar',
    'table', 'target-notes', 'tip', 'title', 'topic', 'unicode', 'warning',
    # Sphinx and Python docs custom ones
    'acks', 'attribute', 'autoattribute', 'autoclass', 'autodata',
    'autoexception', 'autofunction', 'automethod', 'automodule',
    'availability', 'centered', 'cfunction', 'class', 'classmethod', 'cmacro',
    'cmdoption', 'cmember', 'code-block', 'confval', 'cssclass', 'ctype',
    'currentmodule', 'cvar', 'data', 'decorator', 'decoratormethod',
    'deprecated-removed', 'deprecated(?!-removed)', 'describe', 'directive',
    'doctest', 'envvar', 'event', 'exception', 'function', 'glossary',
    'highlight', 'highlightlang', 'impl-detail', 'index', 'literalinclude',
    'method', 'miscnews', 'module', 'moduleauthor', 'opcode', 'pdbcommand',
    'productionlist', 'program', 'role', 'sectionauthor', 'seealso',
    'sourcecode', 'staticmethod', 'tabularcolumns', 'testcode', 'testoutput',
    'testsetup', 'toctree', 'todo', 'todolist', 'versionadded',
    'versionchanged'
]
# fmt: on

roles = [
    "(?<!py):class:",
    "(?<!:c|py):func:",
    "(?<!py):meth:",
    "(?<!:py):mod:",
    ":exc:",
    ":issue:",
    ":attr:",
    ":c:func:",
    ":ref:",
    ":const:",
    ":term:",
    "(?<!:c|py):data:",
    ":keyword:",
    ":file:",
    ":pep:",
    ":c:type:",
    ":c:member:",
    ":option:",
    ":rfc:",
    ":envvar:",
    ":c:data:",
    ":source:",
    ":mailheader:",
    ":program:",
    ":c:macro:",
    ":dfn:",
    ":kbd:",
    ":command:",
    ":mimetype:",
    ":opcode:",
    ":manpage:",
    ":py:data:",
    ":RFC:",
    ":pdbcmd:",
    ":abbr:",
    ":samp:",
    ":token:",
    ":PEP:",
    ":sup:",
    ":py:class:",
    ":menuselection:",
    ":doc:",
    ":sub:",
    ":py:meth:",
    ":newsgroup:",
    ":code:",
    ":py:func:",
    ":makevar:",
    ":guilabel:",
    ":title-reference:",
    ":py:mod:",
    ":download:",
    ":2to3fixer:",
]

all_directives = "(" + "|".join(directives) + ")"
all_roles = "(" + "|".join(roles) + ")"

# Find comments that looks like a directive, like:
# .. versionchanged 3.6
# or
# .. versionchanged: 3.6
# as it should be:
# .. versionchanged:: 3.6
seems_directive_re = re.compile(r"(?<!\.)\.\. %s([^a-z:]|:(?!:))" % all_directives)

# Find directive prefixed with three dots instead of two, like:
# ... versionchanged:: 3.6
# instead of:
# .. versionchanged:: 3.6
three_dot_directive_re = re.compile(r"\.\.\. %s::" % all_directives)

# Find role used with double backticks instead of simple backticks like:
# :const:``None``
# instead of:
# :const:`None`
double_backtick_role = re.compile(r"(?<!``)%s``" % all_roles)


# Find role used with no backticks instead of simple backticks like:
# :const:None
# instead of:
# :const:`None`
role_with_no_backticks = re.compile(r"%s[^` ]" % all_roles)

# Find role glued with another word like:
# the:c:func:`PyThreadState_LeaveTracing` function.
# instead of:
# the :c:func:`PyThreadState_LeaveTracing` function.
role_glued_with_word = re.compile(r"[a-zA-Z]%s" % all_roles)

# Find role missing a column, like:
#    the c:macro:`PY_VERSION_HEX`
# instead of:
#    the :c:macro:`PY_VERSION_HEX`
role_missing_leading_column = re.compile(
    r" %s" % ("(" + "|".join(role[1:] + "`" for role in roles if role[0] == ":") + ")")
)


default_role_re = re.compile(r"(^| )`\w([^`]*?\w)?`($| )")
leaked_markup_re = re.compile(r"[a-z]::\s|`|\.\.\s*\w+:")


checkers = {}

checker_props = {"severity": 1, "falsepositives": False}


def checker(*suffixes, **kwds):
    """Decorator to register a function as a checker."""

    def deco(func):
        for suffix in suffixes:
            checkers.setdefault(suffix, []).append(func)
        for prop in checker_props:
            setattr(func, prop, kwds.get(prop, checker_props[prop]))
        return func

    return deco


@checker(".py", severity=4)
def check_syntax(file, lines):
    """Check Python examples for valid syntax."""
    code = "".join(lines)
    if "\r" in code:
        if os.name != "nt":
            yield 0, "\\r in code file"
        code = code.replace("\r", "")
    try:
        compile(code, file, "exec")
    except SyntaxError as err:
        yield err.lineno, "not compilable: %s" % err


@checker(".rst", severity=2)
def check_suspicious_constructs(file, lines):
    """Check for suspicious reST constructs."""
    for lno, line in enumerate(hide_non_rst_blocks(lines), start=1):
        if seems_directive_re.search(line):
            yield lno, "comment seems to be intended as a directive"
        if three_dot_directive_re.search(line):
            yield lno, "directive should start with two dots, not three."
        if double_backtick_role.search(line):
            yield lno, "role use a single backtick, double backtick found."
        if role_with_no_backticks.search(line):
            yield lno, "role use a single backtick, no backtick found."
        if role_glued_with_word.search(line):
            yield lno, "missing space before role"
        if match := role_missing_leading_column.search(line):
            yield lno, f"missing column before role near {match[0]!r}"
        elif default_role_re.search(line):
            yield lno, "default role used"


@checker(".py", ".rst")
def check_whitespace(file, lines):
    """Check for whitespace and line length issues."""
    for lno, line in enumerate(lines):
        if "\r" in line:
            yield lno + 1, "\\r in line"
        if "\t" in line:
            yield lno + 1, "OMG TABS!!!1"
        if line.rstrip("\n").rstrip(" \t") != line.rstrip("\n"):
            yield lno + 1, "trailing whitespace"


@checker(".rst", severity=0)
def check_line_length(file, lines):
    """Check for line length; this checker is not run by default."""
    for lno, line in enumerate(lines):
        if len(line) > 81:
            # don't complain about tables, links and function signatures
            if (
                line.lstrip()[0] not in "+|"
                and "http://" not in line
                and not line.lstrip().startswith(
                    (".. function", ".. method", ".. cfunction")
                )
            ):
                yield lno + 1, "line too long"


@checker(".html", severity=2, falsepositives=True)
def check_leaked_markup(file, lines):
    """Check HTML files for leaked reST markup; this only works if
    the HTML files have been built.
    """
    for lno, line in enumerate(lines):
        if leaked_markup_re.search(line):
            yield lno + 1, "possibly leaked markup: %r" % line


def is_multiline_non_rst_block(line):
    if line.endswith("..\n"):
        return True
    if line.endswith("::\n"):
        return True
    if re.match(r"^ *\.\. code-block::", line):
        return True
    if re.match(r"^ *.. productionlist::", line):
        return True
    return False


def hide_non_rst_blocks(lines, hidden_block_cb=None):
    """Filters out literal, comments, code blocks, ...

    The filter actually replace "removed" lines by empty lines, so the
    line numbering still make sense.
    """
    in_literal = None
    excluded_lines = []
    for line in lines:
        if in_literal is not None:
            current_indentation = len(re.match(" *", line).group(0))
            if current_indentation > in_literal or line == "\n":
                excluded_lines.append(line)
                line = "\n"  # Hiding line
            else:
                in_literal = None
                if hidden_block_cb:
                    hidden_block_cb("".join(excluded_lines))
                excluded_lines = []
        if in_literal is None and is_multiline_non_rst_block(line):
            in_literal = len(re.match(" *", line).group(0))
            assert excluded_lines == []
        elif re.match(r" *\.\. ", line) and type_of_explicit_markup(line) == "comment":
            line = "\n"
        yield line


def type_of_explicit_markup(line):
    if re.match(fr"\.\. {all_directives}::", line):
        return "directive"
    if re.match(r"\.\. \[[0-9]+\] ", line):
        return "footnote"
    if re.match(r"\.\. \[[^\]]+\] ", line):
        return "citation"
    if re.match(r"\.\. _.*[^_]: ", line):
        return "target"
    if re.match(r"\.\. \|[^\|]*\| ", line):
        return "substitution_definition"
    return "comment"


@checker(".rst", severity=2)
def check_missing_surrogate_space_on_plural(file, lines):
    r"""Check for missing 'backslash-space' between a code sample a letter.

    Good: ``Point``\ s
    Bad: ``Point``s
    """
    in_code_sample = False
    check_next_one = False
    for lno, line in enumerate(hide_non_rst_blocks(lines)):
        tokens = line.split("``")
        for token_no, token in enumerate(tokens):
            if check_next_one:
                if token[0] in ascii_letters:
                    yield lno + 1, f"Missing backslash-space between code sample and {token!r}."
                check_next_one = False
            if token_no == len(tokens) - 1:
                continue
            if in_code_sample:
                check_next_one = True
            in_code_sample = not in_code_sample


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="verbose (print all checked file names)",
    )
    parser.add_argument(
        "-f",
        dest="false_pos",
        action="store_true",
        help="enable checked that yield many false positives",
    )
    parser.add_argument(
        "-s",
        "--severity",
        type=int,
        help="only show problems with severity >= sev",
        default=1,
    )
    parser.add_argument(
        "-i",
        "--ignore",
        action="append",
        help="ignore subdire or file path",
        default=[],
    )
    parser.add_argument(
        "-d",
        "--disable",
        dest="disabled",
        action="append",
        help="disable given checks",
        default=[],
    )
    parser.add_argument("path", default=".", nargs="?")
    args = parser.parse_args(argv[1:])
    return args


def is_disabled(msg, disabled_messages):
    return any(disabled in msg for disabled in disabled_messages)


def walk(path, ignore_list):
    """Wrapper around os.walk with an ignore list.

    It also allow giving a file, thus yielding just that file.
    """
    if isfile(path):
        yield path
        return
    for root, dirs, files in os.walk(path):
        # ignore subdirs in ignore list
        if any(ignore in root for ignore in ignore_list):
            del dirs[:]
            continue
        for file in files:
            file = join(root, file)
            # ignore files in ignore list
            if any(ignore in file for ignore in ignore_list):
                continue
            yield file


def check(filename, text, allow_false_positives=False, severity=1, disabled=()):
    errors = Counter()
    ext = splitext(filename)[1]
    lines = text.splitlines(keepends=True)
    for checker in checkers[ext]:
        if checker.falsepositives and not allow_false_positives:
            continue
        csev = checker.severity
        if csev >= severity:
            for lno, msg in checker(filename, lines):
                if not is_disabled(msg, disabled):
                    print("[%d] %s:%d: %s" % (csev, filename, lno, msg))
                    errors[csev] += 1
    return errors


def main(argv):
    args = parse_args(argv)
    if not exists(args.path):
        print(f"Error: path {args.path} does not exist")
        return 2

    count = Counter()

    for file in walk(args.path, args.ignore):
        if file[:2] == "./":
            file = file[2:]

        ext = splitext(file)[1]
        checkerlist = checkers.get(ext, None)
        if not checkerlist:
            continue

        if args.verbose:
            print("Checking %s..." % file)

        try:
            with open(file, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError as err:
            print("%s: cannot open: %s" % (file, err))
            count[4] += 1
            continue

        count.update(check(file, text, args.false_pos, args.severity, args.disabled))

    if args.verbose:
        print()
    if not count:
        if args.severity > 1:
            print("No problems with severity >= %d found." % args.severity)
        else:
            print("No problems found.")
    else:
        for severity in sorted(count):
            number = count[severity]
            print(
                "%d problem%s with severity %d found."
                % (number, number > 1 and "s" or "", severity)
            )
    return int(bool(count))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
