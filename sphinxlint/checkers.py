import os

import regex as re

from sphinxlint import rst
from sphinxlint.utils import (
    clean_paragraph,
    escape2null,
    hide_non_rst_blocks,
    looks_like_glued,
    match_size,
    paragraphs,
)

all_checkers = {}


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
        all_checkers[func.name] = func
        return func

    return deco


@checker(".py", rst_only=False)
def check_python_syntax(file, lines, options=None):
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


@checker(".rst", ".po")
def check_missing_backtick_after_role(file, lines, options=None):
    """Search for roles missing their closing backticks.

    Bad:  :fct:`foo
    Good: :fct:`foo`
    """
    for paragraph_lno, paragraph in paragraphs(lines):
        if paragraph.count("|") > 4:
            return  # we don't handle tables yet.
        error = rst.ROLE_MISSING_CLOSING_BACKTICK_RE.search(paragraph)
        if error:
            error_offset = paragraph[: error.start()].count("\n")
            yield (
                paragraph_lno + error_offset,
                f"role missing closing backtick: {error.group(0)!r}",
            )


_RST_ROLE_RE = re.compile("``.+?``(?!`).", flags=re.DOTALL)
_END_STRING_SUFFIX_RE = re.compile(rst.END_STRING_SUFFIX)


@checker(".rst", ".po")
def check_missing_space_after_literal(file, lines, options=None):
    r"""Search for inline literals immediately followed by a character.

    Bad:  ``items``s
    Good: ``items``\ s
    """
    for paragraph_lno, paragraph in paragraphs(lines):
        if paragraph.count("|") > 4:
            return  # we don't handle tables yet.
        paragraph = clean_paragraph(paragraph)
        for role in _RST_ROLE_RE.finditer(paragraph):
            if not _END_STRING_SUFFIX_RE.match(role[0][-1]):
                error_offset = paragraph[: role.start()].count("\n")
                yield (
                    paragraph_lno + error_offset,
                    "inline literal missing "
                    f"(escaped) space after literal: {role.group(0)!r}",
                )


_LONE_DOUBLE_BACKTICK_RE = re.compile("(?<!`)``(?!`)")


@checker(".rst", ".po")
def check_unbalanced_inline_literals_delimiters(file, lines, options=None):
    r"""Search for unbalanced inline literals delimiters.

    Bad:  ``hello`` world``
    Good: ``hello`` world
    """
    for paragraph_lno, paragraph in paragraphs(lines):
        if paragraph.count("|") > 4:
            return  # we don't handle tables yet.
        paragraph = clean_paragraph(paragraph)
        for lone_double_backtick in _LONE_DOUBLE_BACKTICK_RE.finditer(paragraph):
            error_offset = paragraph[: lone_double_backtick.start()].count("\n")
            yield (
                paragraph_lno + error_offset,
                "found an unbalanced inline literal markup.",
            )


_ends_with_role_tag = re.compile(rst.ROLE_TAG + "$").search
_starts_with_role_tag = re.compile("^" + rst.ROLE_TAG).search


@checker(".rst", ".po", enabled=False)
def check_default_role(file, lines, options=None):
    """Search for default roles (but they are allowed in many projects).

    Bad:  `print`
    Good: ``print``
    """
    for lno, line in enumerate(lines, start=1):
        line = clean_paragraph(line)
        line = escape2null(line)
        match = rst.INTERPRETED_TEXT_RE.search(line)
        if match:
            before_match = line[: match.start()]
            after_match = line[match.end() :]
            stripped_line = line.strip()
            if (
                stripped_line.startswith("|")
                and stripped_line.endswith("|")
                and stripped_line.count("|") >= 4
                and "|" in match.group(0)
            ):
                return  # we don't handle tables yet.
            if _ends_with_role_tag(before_match):
                # It's not a default role: it ends with a tag.
                continue
            if _starts_with_role_tag(after_match):
                # It's not a default role: it starts with a tag.
                continue
            if match.group(0).startswith("``") and match.group(0).endswith("``"):
                # It's not a default role: it's an inline literal.
                continue
            yield (
                lno,
                "default role used (hint: for inline literals, use double backticks)",
            )


@checker(".rst", ".po")
def check_directive_with_three_dots(file, lines, options=None):
    """Search for directives with three dots instead of two.

    Bad:  ... versionchanged:: 3.6
    Good:  .. versionchanged:: 3.6
    """
    for lno, line in enumerate(lines, start=1):
        if rst.THREE_DOT_DIRECTIVE_RE.search(line):
            yield lno, "directive should start with two dots, not three."


@checker(".rst", ".po")
def check_directive_missing_colons(file, lines, options=None):
    """Search for directive wrongly typed as comments.

    Bad:  .. versionchanged 3.6.
    Good: .. versionchanged:: 3.6
    """
    for lno, line in enumerate(lines, start=1):
        if rst.SEEMS_DIRECTIVE_RE.search(line):
            yield lno, "comment seems to be intended as a directive"


# The difficulty here is that the following is valid:
#    The :literal:`:exc:`Exceptions``
# While this is not:
#    The :literal:`:exc:`Exceptions``s
_ROLE_BODY = rf"([^`]|\s`+|\\`|:{rst.SIMPLENAME}:`([^`]|\s`+|\\`)+`)+"
_ALLOWED_AFTER_ROLE = (
    rst.ASCII_ALLOWED_AFTER_INLINE_MARKUP
    + rst.UNICODE_ALLOWED_AFTER_INLINE_MARKUP
    + r"|\s"
)
_SUSPICIOUS_ROLE = re.compile(
    f":{rst.SIMPLENAME}:`{_ROLE_BODY}`[^{_ALLOWED_AFTER_ROLE}]"
)


@checker(".rst", ".po")
def check_missing_space_after_role(file, lines, options=None):
    r"""Search for roles immediately followed by a character.

    Bad:  :exc:`Exception`s.
    Good: :exc:`Exceptions`\ s
    """
    for lno, line in enumerate(lines, start=1):
        line = clean_paragraph(line)
        role = _SUSPICIOUS_ROLE.search(line)
        if role:
            yield lno, f"role missing (escaped) space after role: {role.group(0)!r}"


@checker(".rst", ".po")
def check_role_without_backticks(file, lines, options=None):
    """Search roles without backticks.

    Bad:  :func:pdb.main
    Good: :func:`pdb.main`
    """
    for lno, line in enumerate(lines, start=1):
        no_backticks = rst.ROLE_WITH_NO_BACKTICKS_RE.search(line)
        if no_backticks:
            yield lno, f"role with no backticks: {no_backticks.group(0)!r}"


@checker(".rst", ".po")
def check_backtick_before_role(file, lines, options=None):
    """Search for roles preceded by a backtick.

    Bad: `:fct:`sum`
    Good: :fct:`sum`
    """
    for lno, line in enumerate(lines, start=1):
        if "`" not in line:
            continue
        if rst.BACKTICK_IN_FRONT_OF_ROLE_RE.search(line):
            yield lno, "superfluous backtick in front of role"


@checker(".rst", ".po")
def check_missing_space_in_hyperlink(file, lines, options=None):
    """Search for hyperlinks missing a space.

    Bad:  `Link text<https://example.com>`_
    Good: `Link text <https://example.com>`_
    """
    for lno, line in enumerate(lines, start=1):
        if "`" not in line:
            continue
        for match in rst.SEEMS_HYPERLINK_RE.finditer(line):
            if not match.group(1):
                yield lno, "missing space before < in hyperlink"


@checker(".rst", ".po")
def check_missing_underscore_after_hyperlink(file, lines, options=None):
    """Search for hyperlinks missing underscore after their closing backtick.

    Bad:  `Link text <https://example.com>`
    Good: `Link text <https://example.com>`_
    """
    for lno, line in enumerate(lines, start=1):
        if "`" not in line:
            continue
        for match in rst.SEEMS_HYPERLINK_RE.finditer(line):
            if not match.group(2):
                yield lno, "missing underscore after closing backtick in hyperlink"


@checker(".rst", ".po")
def check_role_with_double_backticks(file, lines, options=None):
    """Search for roles with double backticks.

    Bad:  :fct:``sum``
    Good: :fct:`sum`

    The hard thing is that :fct:``sum`` is a legitimate
    restructuredtext construction:

    :fct: is just plain text.
    ``sum`` is an inline literal.

    So to properly detect this one we're searching for actual inline
    literals that have a role tag.
    """
    for paragraph_lno, paragraph in paragraphs(lines):
        if "`" not in paragraph:
            continue
        if paragraph.count("|") > 4:
            return  # we don't handle tables yet.
        paragraph = escape2null(paragraph)
        while True:
            inline_literal = min(
                rst.INLINE_LITERAL_RE.finditer(paragraph, overlapped=True),
                key=match_size,
                default=None,
            )
            if inline_literal is None:
                break
            before = paragraph[: inline_literal.start()]
            if _ends_with_role_tag(before):
                error_offset = paragraph[: inline_literal.start()].count("\n")
                yield (
                    paragraph_lno + error_offset,
                    "role use a single backtick, double backtick found.",
                )
            paragraph = (
                paragraph[: inline_literal.start()] + paragraph[inline_literal.end() :]
            )


@checker(".rst", ".po")
def check_missing_space_before_role(file, lines, options=None):
    """Search for missing spaces before roles.

    Bad:  the:fct:`sum`, issue:`123`, c:func:`foo`
    Good: the :fct:`sum`, :issue:`123`, :c:func:`foo`
    """
    for paragraph_lno, paragraph in paragraphs(lines):
        if paragraph.count("|") > 4:
            return  # we don't handle tables yet.
        paragraph = clean_paragraph(paragraph)
        match = rst.ROLE_GLUED_WITH_WORD_RE.search(paragraph)
        if match:
            error_offset = paragraph[: match.start()].count("\n")
            if looks_like_glued(match):
                yield (
                    paragraph_lno + error_offset,
                    f"missing space before role ({match.group(0)}).",
                )
            else:
                yield (
                    paragraph_lno + error_offset,
                    f"role missing opening tag colon ({match.group(0)}).",
                )


@checker(".rst", ".po")
def check_missing_space_before_default_role(file, lines, options=None):
    """Search for missing spaces before default role.

    Bad:  the`sum`
    Good: the `sum`
    """
    for paragraph_lno, paragraph in paragraphs(lines):
        if paragraph.count("|") > 4:
            return  # we don't handle tables yet.
        paragraph = clean_paragraph(paragraph)
        paragraph = rst.INTERPRETED_TEXT_RE.sub("", paragraph)
        for role in rst.inline_markup_gen(
            "`", "`", extra_allowed_before="[^_]"
        ).finditer(paragraph):
            error_offset = paragraph[: role.start()].count("\n")
            context = paragraph[role.start() - 3 : role.end()]
            yield (
                paragraph_lno + error_offset,
                f"missing space before default role: {context!r}.",
            )


_HYPERLINK_REFERENCE_RE = re.compile(r"\S* <https?://[^ ]+>`_")


@checker(".rst", ".po")
def check_hyperlink_reference_missing_backtick(file, lines, options=None):
    """Search for missing backticks in front of hyperlink references.

    Bad:  Misc/NEWS <https://github.com/python/cpython/blob/v3.2.6/Misc/NEWS>`_
    Good: `Misc/NEWS <https://github.com/python/cpython/blob/v3.2.6/Misc/NEWS>`_
    """
    for paragraph_lno, paragraph in paragraphs(lines):
        if paragraph.count("|") > 4:
            return  # we don't handle tables yet.
        paragraph = clean_paragraph(paragraph)
        paragraph = rst.INTERPRETED_TEXT_RE.sub("", paragraph)
        for hyperlink_reference in _HYPERLINK_REFERENCE_RE.finditer(paragraph):
            error_offset = paragraph[: hyperlink_reference.start()].count("\n")
            context = hyperlink_reference.group(0)
            yield (
                paragraph_lno + error_offset,
                f"missing backtick before hyperlink reference: {context!r}.",
            )


@checker(".rst", ".po")
def check_missing_colon_in_role(file, lines, options=None):
    """Search for missing colons in roles.

    Bad:  :issue`123`
    Good: :issue:`123`
    """
    for lno, line in enumerate(lines, start=1):
        match = rst.ROLE_MISSING_RIGHT_COLON_RE.search(line)
        if match:
            yield lno, f"role missing colon before first backtick ({match.group(0)})."


@checker(".py", ".rst", ".po", rst_only=False)
def check_carriage_return(file, lines, options=None):
    r"""Check for carriage returns (\r) in lines."""
    for lno, line in enumerate(lines):
        if "\r" in line:
            yield lno + 1, "\\r in line"


@checker(".py", ".rst", ".po", rst_only=False)
def check_horizontal_tab(file, lines, options=None):
    r"""Check for horizontal tabs (\t) in lines."""
    for lno, line in enumerate(lines):
        if "\t" in line:
            yield lno + 1, "OMG TABS!!!1"


@checker(".py", ".rst", ".po", rst_only=False)
def check_trailing_whitespace(file, lines, options=None):
    """Check for trailing whitespaces at end of lines."""
    for lno, line in enumerate(lines):
        stripped_line = line.rstrip("\n")
        if stripped_line.rstrip(" \t") != stripped_line:
            yield lno + 1, "trailing whitespace"


@checker(".py", ".rst", ".po", rst_only=False)
def check_missing_final_newline(file, lines, options=None):
    """Check that the last line of the file ends with a newline."""
    if lines and not lines[-1].endswith("\n"):
        yield len(lines), "No newline at end of file."


_is_long_interpreted_text = re.compile(r"^\s*\W*(:(\w+:)+)?`.*`\W*$").match
_starts_with_directive_or_hyperlink = re.compile(r"^\s*\.\. ").match
_starts_with_anonymous_hyperlink = re.compile(r"^\s*__ ").match
_is_very_long_string_literal = re.compile(r"^\s*``[^`]+``$").match


@checker(".rst", ".po", enabled=False, rst_only=True)
def check_line_too_long(file, lines, options=None):
    """Check for line length; this checker is not run by default."""
    for lno, line in enumerate(lines):
        # Beware, in `line` we have the trailing newline.
        if len(line) - 1 > options.max_line_length:
            if line.lstrip()[0] in "+|":
                continue  # ignore wide tables
            if _is_long_interpreted_text(line):
                continue  # ignore long interpreted text
            if _starts_with_directive_or_hyperlink(line):
                continue  # ignore directives and hyperlink targets
            if _starts_with_anonymous_hyperlink(line):
                continue  # ignore anonymous hyperlink targets
            if _is_very_long_string_literal(line):
                continue  # ignore a very long literal string
            yield lno + 1, f"Line too long ({len(line) - 1}/{options.max_line_length})"


@checker(".html", enabled=False, rst_only=False)
def check_leaked_markup(file, lines, options=None):
    """Check HTML files for leaked reST markup.

    This only works if the HTML files have been built.
    """
    for lno, line in enumerate(lines):
        if rst.LEAKED_MARKUP_RE.search(line):
            yield lno + 1, f"possibly leaked markup: {line}"


@checker(".rst", ".po", enabled=False)
def check_triple_backticks(file, lines, options=None):
    """Check for triple backticks, like ```Point``` (but it's a valid syntax).

    Bad: ```Point```
    Good: ``Point``

    In reality, triple backticks are valid: ```foo``` gets
    rendered as `foo`, it's at least used by Sphinx to document rst
    syntax, but it's really uncommon.
    """
    for lno, line in enumerate(lines):
        match = rst.TRIPLE_BACKTICKS_RE.search(line)
        if match:
            yield lno + 1, "There's no rst syntax using triple backticks"


_has_bad_dedent = re.compile(" [^ ].*::$").match


@checker(".rst", ".po", rst_only=False)
def check_bad_dedent(file, lines, options=None):
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
            if _has_bad_dedent(line):
                errors.append((block_lineno + lineno, "Bad dedent in block"))

    list(hide_non_rst_blocks(lines, hidden_block_cb=check_block))
    yield from errors


_has_dangling_hyphen = re.compile(r".*[a-z]-$").match


@checker(".rst", rst_only=True)
def check_dangling_hyphen(file, lines, options):
    """Check for lines ending in a hyphen."""
    for lno, line in enumerate(lines):
        stripped_line = line.rstrip("\n")
        if _has_dangling_hyphen(stripped_line):
            yield lno + 1, "Line ends with dangling hyphen"


@checker(".rst", ".po", rst_only=False, enabled=True)
def check_unnecessary_parentheses(filename, lines, options):
    """Check for unnecessary parentheses in :func: and :meth: roles.

    Bad:  :func:`test()`
    Good: :func:`test`
    """
    for lno, line in enumerate(lines, start=1):
        if match := rst.ROLE_WITH_UNNECESSARY_PARENTHESES_RE.search(line):
            yield lno, f"Unnecessary parentheses in {match.group(0).strip()!r}"
