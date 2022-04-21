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

__version__ = "0.2"

import os
import re
import sys
import argparse
from string import ascii_letters
from os.path import join, splitext, exists, isfile
from collections import Counter
from itertools import chain


# The following chars groups are from docutils:
closing_delimiters = "\\\\.,;!?"
delimiters = (
    "\\-/:\u058a\xa1\xb7\xbf\u037e\u0387\u055a-\u055f\u0589"
    "\u05be\u05c0\u05c3\u05c6\u05f3\u05f4\u0609\u060a\u060c"
    "\u060d\u061b\u061e\u061f\u066a-\u066d\u06d4\u0700-\u070d"
    "\u07f7-\u07f9\u0830-\u083e\u0964\u0965\u0970\u0df4\u0e4f"
    "\u0e5a\u0e5b\u0f04-\u0f12\u0f85\u0fd0-\u0fd4\u104a-\u104f"
    "\u10fb\u1361-\u1368\u1400\u166d\u166e\u16eb-\u16ed\u1735"
    "\u1736\u17d4-\u17d6\u17d8-\u17da\u1800-\u180a\u1944\u1945"
    "\u19de\u19df\u1a1e\u1a1f\u1aa0-\u1aa6\u1aa8-\u1aad\u1b5a-"
    "\u1b60\u1c3b-\u1c3f\u1c7e\u1c7f\u1cd3\u2010-\u2017\u2020-"
    "\u2027\u2030-\u2038\u203b-\u203e\u2041-\u2043\u2047-"
    "\u2051\u2053\u2055-\u205e\u2cf9-\u2cfc\u2cfe\u2cff\u2e00"
    "\u2e01\u2e06-\u2e08\u2e0b\u2e0e-\u2e1b\u2e1e\u2e1f\u2e2a-"
    "\u2e2e\u2e30\u2e31\u3001-\u3003\u301c\u3030\u303d\u30a0"
    "\u30fb\ua4fe\ua4ff\ua60d-\ua60f\ua673\ua67e\ua6f2-\ua6f7"
    "\ua874-\ua877\ua8ce\ua8cf\ua8f8-\ua8fa\ua92e\ua92f\ua95f"
    "\ua9c1-\ua9cd\ua9de\ua9df\uaa5c-\uaa5f\uaade\uaadf\uabeb"
    "\ufe10-\ufe16\ufe19\ufe30-\ufe32\ufe45\ufe46\ufe49-\ufe4c"
    "\ufe50-\ufe52\ufe54-\ufe58\ufe5f-\ufe61\ufe63\ufe68\ufe6a"
    "\ufe6b\uff01-\uff03\uff05-\uff07\uff0a\uff0c-\uff0f\uff1a"
    "\uff1b\uff1f\uff20\uff3c\uff61\uff64\uff65"
)
closers = (
    "\"')>\\]}\u0f3b\u0f3d\u169c\u2046\u207e\u208e\u232a\u2769"
    "\u276b\u276d\u276f\u2771\u2773\u2775\u27c6\u27e7\u27e9\u27eb"
    "\u27ed\u27ef\u2984\u2986\u2988\u298a\u298c\u298e\u2990\u2992"
    "\u2994\u2996\u2998\u29d9\u29db\u29fd\u2e23\u2e25\u2e27\u2e29"
    "\u3009\u300b\u300d\u300f\u3011\u3015\u3017\u3019\u301b\u301e"
    "\u301f\ufd3f\ufe18\ufe36\ufe38\ufe3a\ufe3c\ufe3e\ufe40\ufe42"
    "\ufe44\ufe48\ufe5a\ufe5c\ufe5e\uff09\uff3d\uff5d\uff60\uff63"
    "\xbb\u2019\u201d\u203a\u2e03\u2e05\u2e0a\u2e0d\u2e1d\u2e21"
    "\u201b\u201f\xab\u2018\u201c\u2039\u2e02\u2e04\u2e09\u2e0c"
    "\u2e1c\u2e20\u201a\u201e"
)
openers = (
    "\"'(<\\[{\u0f3a\u0f3c\u169b\u2045\u207d\u208d\u2329\u2768"
    "\u276a\u276c\u276e\u2770\u2772\u2774\u27c5\u27e6\u27e8\u27ea"
    "\u27ec\u27ee\u2983\u2985\u2987\u2989\u298b\u298d\u298f\u2991"
    "\u2993\u2995\u2997\u29d8\u29da\u29fc\u2e22\u2e24\u2e26\u2e28"
    "\u3008\u300a\u300c\u300e\u3010\u3014\u3016\u3018\u301a\u301d"
    "\u301d\ufd3e\ufe17\ufe35\ufe37\ufe39\ufe3b\ufe3d\ufe3f\ufe41"
    "\ufe43\ufe47\ufe59\ufe5b\ufe5d\uff08\uff3b\uff5b\uff5f\uff62"
    "\xab\u2018\u201c\u2039\u2e02\u2e04\u2e09\u2e0c\u2e1c\u2e20"
    "\u201a\u201e\xbb\u2019\u201d\u203a\u2e03\u2e05\u2e0a\u2e0d"
    "\u2e1d\u2e21\u201b\u201f"
)


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


all_directives = "(" + "|".join(directives) + ")"
before_role = r"(^|(?<=[\s(/'{\[*-]))"
simplename = r"(?:(?!_)\w)+(?:[-._+:](?:(?!_)\w)+)*"
role_head = r"({}:{}:)".format(before_role, simplename)  # A role, with a clean start

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
double_backtick_role = re.compile(r"(?<!``)%s``" % role_head)

start_string_prefix = "(^|(?<=\\s|[%s%s|]))" % (openers, delimiters)
end_string_suffix = "($|(?=\\s|[\x00%s%s%s|]))" % (
    closing_delimiters,
    delimiters,
    closers,
)

# Find role glued with another word like:
#     the:c:func:`PyThreadState_LeaveTracing` function.
# instead of:
#     the :c:func:`PyThreadState_LeaveTracing` function.
#
# Also finds roles missing their leading column like:
#     issue:`123`
# instead of:
#     :issue:`123`
role_glued_with_word = re.compile(r"(^|\s)(?!:){}:`(?!`)".format(simplename))


role_with_no_backticks = re.compile(
    r"(^|\s):{}:(?![`:])[^\s`]+(\s|$)".format(simplename)
)

# Find role missing middle column, like:
#    The :issue`123` is ...
role_missing_right_column = re.compile(r"(^|\s):{}`(?!`)".format(simplename))

# Find role glued with a plural mark or something like:
#    The :exc:`Exception`s
# instead of:
#    The :exc:`Exceptions`\ s
role_body = r"([^`]|\s`+|\\`)+"
role_missing_surrogate_escape = re.compile(
    r"{}`{}(?<![\\\s`])`(?!{})".format(role_head, role_body, end_string_suffix)
)

# TODO: cover more cases
# https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#toc-entry-44
default_role_re = re.compile(r"(^| )`\w([^`]*?\w)?`($| )")

seems_hyperlink_re = re.compile(r"`[^`]*?(\s?)<https?://[^`]+>`(_?)")

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


def is_in_a_table(error, line):
    return "|" in line[: error.start()] and "|" in line[error.end() :]


role_missing_closing_backtick = re.compile(rf"({role_head}`{role_body})[^`]*$")


def check_paragraph(paragraph_lno, paragraph):
    error = role_missing_closing_backtick.search(paragraph)
    if error and not "|" in paragraph:
        error_offset = paragraph[: error.start()].count("\n")
        yield paragraph_lno + error_offset, f"role missing closing backtick: {error.group(0)!r}"


@checker(".rst", severity=2)
def check_suspicious_constructs_in_paragraphs(file, lines):
    """Check for suspicious reST constructs at paragraph level."""
    paragraph = []
    paragraph_lno = 1
    for lno, line in enumerate(hide_non_rst_blocks(lines), start=1):
        if line != "\n":
            paragraph.append(line)
        elif paragraph:
            yield from check_paragraph(paragraph_lno, "".join(paragraph))
            paragraph = []
            paragraph_lno = lno
    if paragraph:
        yield from check_paragraph(paragraph_lno, "".join(paragraph))


backtick_in_front_of_role = re.compile(r"(^|\s)`:{}:`{}`".format(simplename, role_body))


@checker(".rst", severity=2)
def check_suspicious_constructs(file, lines):
    """Check for suspicious reST constructs."""
    for lno, line in enumerate(hide_non_rst_blocks(lines), start=1):
        if backtick_in_front_of_role.search(line):
            yield lno, "superfluous backtick in front of role"
        if seems_directive_re.search(line):
            yield lno, "comment seems to be intended as a directive"
        if three_dot_directive_re.search(line):
            yield lno, "directive should start with two dots, not three."
        for match in seems_hyperlink_re.finditer(line):
            if not match.group(1):
                yield lno, "missing space before < in hyperlink"
            if not match.group(2):
                yield lno, "missing underscore after closing backtick in hyperlink"
        if double_backtick_role.search(line):
            yield lno, "role use a single backtick, double backtick found."
        if role_glued_with_word.search(line):
            yield lno, "missing space before role"
        no_backticks = role_with_no_backticks.search(line)
        if no_backticks:
            yield lno, f"role with no backticks: {no_backticks.group(0)!r}"
        if role_missing_right_column.search(line):
            yield lno, "role missing column before first backtick."
        error = role_missing_surrogate_escape.search(line)
        if error and not is_in_a_table(error, line):
            yield lno, f"role missing surrogate escape before plural: {error.group(0)!r}"
        elif default_role_re.search(line):
            yield lno, "default role used (hint: for inline code, use double backticks)"


@checker(".py", ".rst")
def check_whitespace(file, lines):
    """Check for whitespace and line length issues."""
    lno = line = None
    for lno, line in enumerate(lines):
        if "\r" in line:
            yield lno + 1, "\\r in line"
        if "\t" in line:
            yield lno + 1, "OMG TABS!!!1"
        if line.rstrip("\n").rstrip(" \t") != line.rstrip("\n"):
            yield lno + 1, "trailing whitespace"
    if line is not None:
        if not line.endswith("\n"):
            yield lno, "No newline at end of file (no-newline-at-end-of-file)."


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
    block_line_start = None
    for lineno, line in enumerate(lines, start=1):
        if in_literal is not None:
            current_indentation = len(re.match(" *", line).group(0))
            if current_indentation > in_literal or line == "\n":
                excluded_lines.append(line if line == "\n" else line[in_literal:])
                line = "\n"  # Hiding line
            else:
                in_literal = None
                if hidden_block_cb:
                    hidden_block_cb(block_line_start, "".join(excluded_lines))
                excluded_lines = []
        if in_literal is None and is_multiline_non_rst_block(line):
            in_literal = len(re.match(" *", line).group(0))
            block_line_start = lineno
            assert excluded_lines == []
        elif re.match(r" *\.\. ", line) and type_of_explicit_markup(line) == "comment":
            line = "\n"
        yield line
    if excluded_lines and hidden_block_cb:
        hidden_block_cb(block_line_start, "".join(excluded_lines))


def type_of_explicit_markup(line):
    if re.match(rf"\.\. {all_directives}::", line):
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


glued_inline_literals = re.compile(
    r"{}(``[^`]+?(?!{})``)(?!{})".format(
        start_string_prefix, start_string_prefix, end_string_suffix
    )
)


@checker(".rst", severity=2)
def check_missing_surrogate_space_on_plural(file, lines):
    r"""Check for missing 'backslash-space' between a code sample a letter.

    Good: ``Point``\ s
    Bad: ``Point``s
    """
    for lno, line in enumerate(hide_non_rst_blocks(lines)):
        match = glued_inline_literals.search(line)
        if match and match.start() != 0:
            literal = match.group(2)
            yield lno + 1, f"Missing backslash-space between literal {literal} (column {match.start()!r})."


triple_backticks = re.compile(
    r"(?:{})```[^`]+?(?<!{})```(?:{})".format(
        start_string_prefix, start_string_prefix, end_string_suffix
    )
)


@checker(".rst", severity=2)
def check_triple_backticks(file, lines):
    f"""Check for triple backticks.

    Good: ``Point``
    Bad: ```Point```
    """
    for lno, line in enumerate(hide_non_rst_blocks(lines)):
        match = triple_backticks.search(line)
        if match:
            yield lno + 1, f"There's no rst syntax using triple backticks"


@checker(".rst", severity=1)
def check_bad_dedent_in_block(file, lines):
    """Check for dedent not being enough in code blocks."""

    errors = []

    def check_block(block_lineno, block):
        for lineno, line in enumerate(block.splitlines()):
            if re.match(" [^ ].*::$", line):
                errors.append((block_lineno + lineno, "Bad dedent in block"))

    list(hide_non_rst_blocks(lines, hidden_block_cb=check_block))
    for error in errors:
        yield error


def parse_args(argv=None):
    if argv is None:
        argv = sys.argv
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
    parser.add_argument("paths", default=".", nargs="*")
    args = parser.parse_args(argv[1:])
    return args


def is_disabled(msg, disabled_messages):
    return any(disabled in msg for disabled in disabled_messages)


def walk(path, ignore_list):
    """Wrapper around os.walk with an ignore list.

    It also allow giving a file, thus yielding just that file.
    """
    if isfile(path):
        yield path if path[:2] != "./" else path[2:]
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
            yield file if file[:2] != "./" else file[2:]


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


def main(argv=None):
    args = parse_args(argv)

    for path in args.paths:
        if not exists(path):
            print(f"Error: path {path} does not exist")
            return 2

    count = Counter()

    for file in chain.from_iterable(walk(path, args.ignore) for path in args.paths):
        ext = splitext(file)[1]
        if ext not in checkers:
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
        except UnicodeDecodeError as err:
            print("%s: cannot decode as UTF-8: %s" % (file, err))
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
    sys.exit(int(bool(count)))


if __name__ == "__main__":
    main()
