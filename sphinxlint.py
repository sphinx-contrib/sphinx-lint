#!/usr/bin/env python3

# Check for stylistic and formal issues in .rst and .py
# files included in the documentation.
#
# 01/2009, Georg Brandl

# TODO: - wrong versions in versionadded/changed
#       - wrong markup after versionchanged directive

"""Sphinx rst linter.
"""

__version__ = "0.4.1"

import argparse
import multiprocessing
import os
import re
import sys
from collections import Counter
from functools import reduce
from itertools import chain, starmap
from os.path import exists, isfile, join, splitext

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
role_head = rf"({before_role}:{simplename}:)"  # A role, with a clean start

# Find comments that look like a directive, like:
# .. versionchanged 3.6
# or
# .. versionchanged: 3.6
# as it should be:
# .. versionchanged:: 3.6
seems_directive_re = re.compile(rf"^\s*(?<!\.)\.\. {all_directives}([^a-z:]|:(?!:))")

# Find directive prefixed with three dots instead of two, like:
# ... versionchanged:: 3.6
# instead of:
# .. versionchanged:: 3.6
three_dot_directive_re = re.compile(rf"\.\.\. {all_directives}::")

# Find role used with double backticks instead of simple backticks like:
# :const:``None``
# instead of:
# :const:`None`
double_backtick_role = re.compile(rf"(?<!``){role_head}``")

start_string_prefix = f"(^|(?<=\\s|[{openers}{delimiters}|]))"
end_string_suffix = f"($|(?=\\s|[\x00{closing_delimiters}{delimiters}{closers}|]))"

# Find role glued with another word like:
#     the:c:func:`PyThreadState_LeaveTracing` function.
# instead of:
#     the :c:func:`PyThreadState_LeaveTracing` function.
#
# Also finds roles missing their leading colon like:
#     issue:`123`
# instead of:
#     :issue:`123`
role_glued_with_word = re.compile(rf"(^|\s)(?!:){simplename}:`(?!`)")


role_with_no_backticks = re.compile(rf"(^|\s):{simplename}:(?![`:])[^\s`]+(\s|$)")

# Find role missing middle colon, like:
#    The :issue`123` is ...
role_missing_right_colon = re.compile(rf"(^|\s):{simplename}`(?!`)")

# TODO: cover more cases
# https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#toc-entry-44
default_role_re = re.compile(r"(^| )`\w([^`]*?\w)?`($| )")

seems_hyperlink_re = re.compile(r"`[^`]+?(\s?)<https?://[^`]+>`(_?)")

leaked_markup_re = re.compile(r"[a-z]::\s|`|\.\.\s*\w+:")


checkers = {}


def checker(*suffixes, **kwds):
    """Decorator to register a function as a checker."""
    checker_props = {"enabled": True, "rst_only": True}

    def deco(func):
        if not func.__name__.startswith("check_"):
            raise ValueError("Checker names should start with 'check_'.")
        for prop, default_value in checker_props.items():
            setattr(func, prop, kwds.get(prop, default_value))
        func.suffixes = suffixes
        func.name = func.__name__[len("check_") :].replace("_", "-")
        checkers[func.name] = func
        return func

    return deco


@checker(".py", rst_only=False)
def check_python_syntax(file, lines):
    """Search invalid syntax in Python examples."""
    code = "".join(lines)
    if "\r" in code:
        if os.name != "nt":
            yield 0, "\\r in code file"
        code = code.replace("\r", "")
    try:
        compile(code, file, "exec")
    except SyntaxError as err:
        yield err.lineno, f"not compilable: {err}"


def is_in_a_table(error, line):
    return "|" in line[: error.start()] and "|" in line[error.end() :]


role_missing_closing_backtick = re.compile(rf"({role_head}`[^`]+?)[^`]*$")


@checker(".rst")
def check_missing_backtick_after_role(file, lines):
    """Search for roles missing their closing backticks.

    Bad:  :fct:`foo
    Good: :fct:`foo`
    """
    for paragraph_lno, paragraph in paragraphs(lines):
        if paragraph.count("|") > 4:
            return  # we don't handle tables yet.
        error = role_missing_closing_backtick.search(paragraph)
        if error:
            error_offset = paragraph[: error.start()].count("\n")
            yield paragraph_lno + error_offset, f"role missing closing backtick: {error.group(0)!r}"


@checker(".rst")
def check_missing_space_after_literal(file, lines):
    r"""Search for inline literals immediately followed by a character.

    Bad:  ``items``s
    Good: ``items``\ s
    """
    for paragraph_lno, paragraph in paragraphs(lines):
        if paragraph.count("|") > 4:
            return  # we don't handle tables yet.
        paragraph_without_roles = re.sub(normal_role, "", paragraph).replace("````", "")
        for role in re.finditer(
            "``.+?``(?!`).", paragraph_without_roles, flags=re.DOTALL
        ):
            if not re.match(end_string_suffix, role.group(0)[-1]):
                error_offset = paragraph[: role.start()].count("\n")
                yield (
                    paragraph_lno + error_offset,
                    "inline literal missing "
                    f"(escaped) space after literal: {role.group(0)!r}",
                )


def paragraphs(lines):
    """Yield (paragraph_line_no, paragraph_text) pairs describing
    paragraphs of the given lines.
    """
    paragraph = []
    paragraph_lno = 1
    for lno, line in enumerate(lines, start=1):
        if line != "\n":
            paragraph.append(line)
        elif paragraph:
            yield paragraph_lno, "".join(paragraph)
            paragraph = []
            paragraph_lno = lno
    if paragraph:
        yield paragraph_lno, "".join(paragraph)


role_body = rf"([^`]|\s`+|\\`|:{simplename}:`([^`]|\s`+|\\`)+`)+"
normal_role = f":{simplename}:`{role_body}`"
backtick_in_front_of_role = re.compile(rf"(^|\s)`:{simplename}:`{role_body}`")


@checker(".rst", enabled=False)
def check_default_role(file, lines):
    """Search for default roles (but they are allowed in many projects).

    Bad:  `print`
    Good: ``print``
    """
    for lno, line in enumerate(lines, start=1):
        if default_role_re.search(line):
            yield lno, "default role used (hint: for inline literals, use double backticks)"


@checker(".rst")
def check_directive_with_three_dots(file, lines):
    """Search for directives with three dots instead of two.

    Bad:  ... versionchanged:: 3.6
    Good:  .. versionchanged:: 3.6
    """
    for lno, line in enumerate(lines, start=1):
        if three_dot_directive_re.search(line):
            yield lno, "directive should start with two dots, not three."


@checker(".rst")
def check_directive_missing_colons(file, lines):
    """Search for directive wrongly typed as comments.

    Bad:  .. versionchanged 3.6.
    Good: .. versionchanged:: 3.6
    """
    for lno, line in enumerate(lines, start=1):
        if seems_directive_re.search(line):
            yield lno, "comment seems to be intended as a directive"


@checker(".rst")
def check_missing_space_after_role(file, lines):
    r"""Search for roles immediately followed by a character.

    Bad:  :exc:`Exception`s.
    Good: :exc:`Exceptions`\ s
    """
    # The difficulty here is that the following is valid:
    #    The :literal:`:exc:`Exceptions``
    # While this is not:
    #    The :literal:`:exc:`Exceptions``s
    for lno, line in enumerate(lines, start=1):
        line = re.sub("``.*?``", "", line).replace("````", "")
        role = re.search(rf"{normal_role}s", line)
        if role:
            yield lno, f"role missing (escaped) space after role: {role.group(0)!r}"


@checker(".rst")
def check_role_without_backticks(file, lines):
    """Search roles without backticks.

    Bad:  :func:pdb.main
    Good: :func:`pdb.main`
    """
    for lno, line in enumerate(lines, start=1):
        no_backticks = role_with_no_backticks.search(line)
        if no_backticks:
            yield lno, f"role with no backticks: {no_backticks.group(0)!r}"


@checker(".rst")
def check_backtick_before_role(file, lines):
    """Search for roles preceded by a backtick.

    Bad: `:fct:`sum`
    Good: :fct:`sum`
    """
    for lno, line in enumerate(lines, start=1):
        if "`" not in line:
            continue
        if backtick_in_front_of_role.search(line):
            yield lno, "superfluous backtick in front of role"


@checker(".rst")
def check_missing_space_in_hyperlink(file, lines):
    """Search for hyperlinks missing a space.

    Bad:  `Link text<https://example.com>_`
    Good: `Link text <https://example.com>_`
    """
    for lno, line in enumerate(lines, start=1):
        if "`" not in line:
            continue
        for match in seems_hyperlink_re.finditer(line):
            if not match.group(1):
                yield lno, "missing space before < in hyperlink"


@checker(".rst")
def check_missing_underscore_after_hyperlink(file, lines):
    """Search for hyperlinks missing underscore after their closing backtick.

    Bad:  `Link text <https://example.com>`
    Good: `Link text <https://example.com>`_
    """
    for lno, line in enumerate(lines, start=1):
        if "`" not in line:
            continue
        for match in seems_hyperlink_re.finditer(line):
            if not match.group(2):
                yield lno, "missing underscore after closing backtick in hyperlink"


@checker(".rst")
def check_role_with_double_backticks(file, lines):
    """Search for roles with double backticks.

    Bad:  :fct:``sum``
    Good: :fct:`sum`
    """
    for lno, line in enumerate(lines, start=1):
        if "`" not in line:
            continue
        if double_backtick_role.search(line):
            yield lno, "role use a single backtick, double backtick found."


@checker(".rst")
def check_missing_space_before_role(file, lines):
    """Search for spaces missing before roles.

    Bad:  the:fct:`sum`
    Good: the :fct:`sum`
    """
    for lno, line in enumerate(lines, start=1):
        if "`" not in line:
            continue
        if role_glued_with_word.search(line):
            yield lno, "missing space before role"


@checker(".rst")
def check_missing_colon_in_role(file, lines):
    """Search for roles missing a colon.

    Bad:  :issue`123`
    Good: :issue:`123`
    """
    for lno, line in enumerate(lines, start=1):
        if role_missing_right_colon.search(line):
            yield lno, "role missing colon before first backtick."


@checker(".py", ".rst", rst_only=False)
def check_carriage_return(file, lines):
    r"""Check for carriage returns (\r) in lines."""
    for lno, line in enumerate(lines):
        if "\r" in line:
            yield lno + 1, "\\r in line"


@checker(".py", ".rst", rst_only=False)
def check_horizontal_tab(file, lines):
    r"""Check for horizontal tabs (\t) in lines."""
    for lno, line in enumerate(lines):
        if "\t" in line:
            yield lno + 1, "OMG TABS!!!1"


@checker(".py", ".rst", rst_only=False)
def check_trailing_whitespace(file, lines):
    """Check for trailing whitespaces at end of lines."""
    for lno, line in enumerate(lines):
        stripped_line = line.rstrip("\n")
        if stripped_line.rstrip(" \t") != stripped_line:
            yield lno + 1, "trailing whitespace"


@checker(".py", ".rst", rst_only=False)
def check_missing_final_newline(file, lines):
    """Check if the last line ends with a newline, like any other lines."""
    if lines and not lines[-1].endswith("\n"):
        yield len(lines), "No newline at end of file."


@checker(".rst", enabled=False, rst_only=False)
def check_line_too_long(file, lines):
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


@checker(".html", enabled=False, rst_only=False)
def check_leaked_markup(file, lines):
    """Check HTML files for leaked reST markup.

    This only works if the HTML files have been built.
    """
    for lno, line in enumerate(lines):
        if leaked_markup_re.search(line):
            yield lno + 1, f"possibly leaked markup: {line}"


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
    output = []
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
            assert not excluded_lines
        elif re.match(r" *\.\. ", line) and type_of_explicit_markup(line) == "comment":
            line = "\n"
        output.append(line)
    if excluded_lines and hidden_block_cb:
        hidden_block_cb(block_line_start, "".join(excluded_lines))
    return output


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


triple_backticks = re.compile(
    rf"(?:{start_string_prefix})```[^`]+?(?<!{start_string_prefix})```(?:{end_string_suffix})"
)


@checker(".rst", enabled=False)
def check_triple_backticks(file, lines):
    """Check for triple backticks, like ```Point``` (but it's a valid syntax).

    Bad: ```Point```
    Good: ``Point``

    In reality, triple backticks are valid: ```foo``` gets
    rendered as `foo`, it's at least used by Sphinx to document rst
    syntax, but it's really uncommon.
    """
    for lno, line in enumerate(lines):
        match = triple_backticks.search(line)
        if match:
            yield lno + 1, "There's no rst syntax using triple backticks"


@checker(".rst", rst_only=False)
def check_bad_dedent(file, lines):
    """Check for mis-alignment in indentation in code blocks.

    |A 5 lines block::
    |
    |    Hello!
    |
    | Looks like another block::
    |
    |    But in fact it's not due to the leading space.
    """

    errors = []

    def check_block(block_lineno, block):
        for lineno, line in enumerate(block.splitlines()):
            if re.match(" [^ ].*::$", line):
                errors.append((block_lineno + lineno, "Bad dedent in block"))

    list(hide_non_rst_blocks(lines, hidden_block_cb=check_block))
    yield from errors


def parse_args(argv=None):
    if argv is None:
        argv = sys.argv
    parser = argparse.ArgumentParser(description=__doc__)

    enabled_checkers_names = {
        checker.name for checker in checkers.values() if checker.enabled
    }

    class EnableAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            if values == "all":
                enabled_checkers_names.update(set(checkers.keys()))
            else:
                enabled_checkers_names.update(values.split(","))

    class DisableAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            if values == "all":
                enabled_checkers_names.clear()
            else:
                enabled_checkers_names.difference_update(values.split(","))

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="verbose (print all checked file names)",
    )
    parser.add_argument(
        "-i",
        "--ignore",
        action="append",
        help="ignore subdir or file path",
        default=[],
    )
    parser.add_argument(
        "-d",
        "--disable",
        action=DisableAction,
        help='comma-separated list of checks to disable. Give "all" to disable them all. '
        "Can be used in conjunction with --enable (it's evaluated left-to-right). "
        '"--disable all --enable trailing-whitespace" can be used to enable a '
        "single check.",
    )
    parser.add_argument(
        "-e",
        "--enable",
        action=EnableAction,
        help='comma-separated list of checks to enable. Give "all" to enable them all. '
        "Can be used in conjunction with --disable (it's evaluated left-to-right). "
        '"--enable all --disable trailing-whitespace" can be used to enable '
        "all but one check.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List enabled checkers and exit. "
        "Can be used to see which checkers would be used with a given set of "
        "--enable and --disable options.",
    )
    parser.add_argument("paths", default=".", nargs="*")
    args = parser.parse_args(argv[1:])
    try:
        enabled_checkers = {checkers[name] for name in enabled_checkers_names}
    except KeyError as err:
        print(f"Unknown checker: {err.args[0]}.")
        sys.exit(2)
    return enabled_checkers, args


def walk(path, ignore_list):
    """Wrapper around os.walk with an ignore list.

    It also allows giving a file, thus yielding just that file.
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


def check_text(filename, text, checkers):
    errors = Counter()
    ext = splitext(filename)[1]
    checkers = {checker for checker in checkers if ext in checker.suffixes}
    lines = text.splitlines(keepends=True)
    if any(checker.rst_only for checker in checkers):
        lines_with_rst_only = hide_non_rst_blocks(lines)
    for check in checkers:
        if ext not in check.suffixes:
            continue
        for lno, msg in check(
            filename, lines_with_rst_only if check.rst_only else lines
        ):
            print(f"{filename}:{lno}: {msg} ({check.name})")
            errors[check.name] += 1
    return errors


def check_file(filename, checkers):
    ext = splitext(filename)[1]
    if not any(ext in checker.suffixes for checker in checkers):
        return Counter()
    try:
        with open(filename, encoding="utf-8") as f:
            text = f.read()
    except OSError as err:
        print(f"{filename}: cannot open: {err}")
        return Counter({4: 1})
    except UnicodeDecodeError as err:
        print(f"{filename}: cannot decode as UTF-8: {err}")
        return Counter({4: 1})
    return check_text(filename, text, checkers)


def main(argv=None):
    enabled_checkers, args = parse_args(argv)
    if args.list:
        if not enabled_checkers:
            print("No checkers selected.")
            return 0
        print(f"{len(enabled_checkers)} checkers selected:")
        for check in sorted(enabled_checkers, key=lambda fct: fct.name):
            if args.verbose:
                print(f"- {check.name}: {check.__doc__}")
            else:
                print(f"- {check.name}: {check.__doc__.splitlines()[0]}")
        if not args.verbose:
            print("\n(Use `--list --verbose` to know more about each check)")
        return 0

    for path in args.paths:
        if not exists(path):
            print(f"Error: path {path} does not exist")
            return 2

    todo = [
        (path, enabled_checkers)
        for path in chain.from_iterable(walk(path, args.ignore) for path in args.paths)
    ]

    if len(todo) < 8:
        results = starmap(check_file, todo)
    else:
        with multiprocessing.Pool() as pool:
            results = pool.starmap(check_file, todo)
            pool.close()
            pool.join()

    count = reduce(Counter.__add__, results)

    if not count:
        print("No problems found.")
    return int(bool(count))


if __name__ == "__main__":
    sys.exit(main())
