"""Just a bunch of utility functions for sphinxlint."""

from functools import lru_cache

import regex as re
from polib import pofile

from sphinxlint import rst

PER_FILE_CACHES = []


def per_file_cache(func):
    memoized_func = lru_cache(maxsize=None)(func)
    PER_FILE_CACHES.append(memoized_func)
    return memoized_func


def match_size(re_match):
    return re_match.end() - re_match.start()


def _clean_heuristic(paragraph, regex):
    """Remove the regex from the paragraph.

    The remove starts by most "credible" ones (here lies the dragons).

    To remove `(.*)` from `(abc def ghi (jkl)`, a bad move consists of
    removing everything (eating a lone `(`), while the most credible
    action to take is to remove `(jkl)`, leaving a lone `(`.
    """
    while True:
        candidate = min(
            regex.finditer(paragraph, overlapped=True), key=match_size, default=None
        )
        if candidate is None:
            return paragraph
        paragraph = paragraph[: candidate.start()] + paragraph[candidate.end() :]


@per_file_cache
def clean_paragraph(paragraph):
    """Removes all good constructs, so detectors can focus on bad ones.

    It removes all well formed inline literals, inline internal
    targets, and roles.
    """
    paragraph = escape2null(paragraph)
    paragraph = _clean_heuristic(paragraph, rst.INLINE_LITERAL_RE)
    paragraph = _clean_heuristic(paragraph, rst.INLINE_INTERNAL_TARGET_RE)
    paragraph = _clean_heuristic(paragraph, rst.HYPERLINK_REFERENCES_RE)
    paragraph = _clean_heuristic(paragraph, rst.ANONYMOUS_HYPERLINK_REFERENCES_RE)
    paragraph = rst.NORMAL_ROLE_RE.sub("", paragraph)
    return paragraph.replace("\x00", "\\")


@per_file_cache
def escape2null(text):
    r"""Return a string with escape-backslashes converted to nulls.

    It ease telling appart escaping-backslashes and normal backslashes
    in regex.

    For example : \\\\\\` is hard to match, even with the eyes, it's
    hard to know which backslash escapes which backslash, and it's
    very hard to know if the backtick is escaped.

    By replacing the escaping backslashes with another character they
    become easy to spot:

    0\0\0\`

    (This example uses zeros for readability but the function actually
    uses null bytes, \x00.)

    So we easily see that the backtick is **not** escaped: it's
    preceded by a backslash, not an escaping backslash.
    """
    parts = []
    start = 0
    while True:
        found = text.find("\\", start)
        if found == -1:
            parts.append(text[start:])
            return "".join(parts)
        parts.append(text[start:found])
        parts.append("\x00" + text[found + 1 : found + 2])
        start = found + 2  # skip character after escape


@per_file_cache
def paragraphs(lines):
    """Yield (paragraph_line_no, paragraph_text) pairs describing
    paragraphs of the given lines.
    """
    output = []
    paragraph = []
    paragraph_lno = 1
    for lno, line in enumerate(lines, start=1):
        if line != "\n":
            if not paragraph:
                # save the lno of the first line of the para
                paragraph_lno = lno
            paragraph.append(line)
        elif paragraph:
            output.append((paragraph_lno, "".join(paragraph)))
            paragraph = []
    if paragraph:
        output.append((paragraph_lno, "".join(paragraph)))
    return tuple(output)


def looks_like_glued(match):
    """Tell appart glued tags and tags with a missing colon.

    In one case we can have:

        the:issue:`123`, it's clearly a missing space before the role tag.

    should return True in this case.

    In another case we can have:

        c:func:`foo`, it's a missing colon before the tag.

    should return False in this case.
    """
    match_string = match.group(0)
    if match_string.count(":") == 1:
        # With a single : there's no choice, another : is missing.
        return False
    known_start_tag = {"c", "py"}
    if re.match(" *(" + "|".join(known_start_tag) + "):", match_string):
        # Before c:anything:` or py:anything:` we can bet it's a missing colon.
        return False
    # In other cases it's probably a glued word.
    return True


_START_OF_COMMENT_BLOCK_RE = re.compile(r"^\s*\.\.$")
_PRODUCTION_LIST_DIRECTIVE_RE = re.compile(r"^ *.. productionlist::")
_COMMENT_RE = re.compile(r"^ *\.\. ")


def is_multiline_non_rst_block(line):
    """Returns True if the next lines are an indented literal block."""
    if _START_OF_COMMENT_BLOCK_RE.search(line):
        return True
    if rst.DIRECTIVES_CONTAINING_RST_RE.match(line):
        return False
    if rst.DIRECTIVES_CONTAINING_ARBITRARY_CONTENT_RE.match(line):
        return True
    if _PRODUCTION_LIST_DIRECTIVE_RE.search(line):
        return True
    if _COMMENT_RE.search(line) and type_of_explicit_markup(line) == "comment":
        return True
    if line.endswith("::\n"):  # It's a literal block
        return True
    return False


_ZERO_OR_MORE_SPACES_RE = re.compile(" *")


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
            current_indentation = len(_ZERO_OR_MORE_SPACES_RE.match(line)[0])
            if current_indentation > in_literal or line == "\n":
                excluded_lines.append(line if line == "\n" else line[in_literal:])
                line = "\n"  # Hiding line
            else:
                in_literal = None
                if hidden_block_cb:
                    hidden_block_cb(block_line_start, "".join(excluded_lines))
                excluded_lines = []
        if in_literal is None and is_multiline_non_rst_block(line):
            in_literal = len(_ZERO_OR_MORE_SPACES_RE.match(line)[0])
            block_line_start = lineno
            assert not excluded_lines
            if type_of_explicit_markup(line) == "comment" and _COMMENT_RE.search(line):
                line = "\n"
        output.append(line)
    if excluded_lines and hidden_block_cb:
        hidden_block_cb(block_line_start, "".join(excluded_lines))
    return tuple(output)


_starts_with_directive_marker = re.compile(rf"\.\. {rst.ALL_DIRECTIVES}::").match
_starts_with_footnote_marker = re.compile(r"\.\. \[[0-9]+\] ").match
_starts_with_citation_marker = re.compile(r"\.\. \[[^\]]+\] ").match
_starts_with_target = re.compile(r"\.\. _.*[^_]: ").match
_starts_with_substitution_definition = re.compile(r"\.\. \|[^\|]*\| ").match


@per_file_cache
def type_of_explicit_markup(line):
    """Tell apart various explicit markup blocks."""
    line = line.lstrip()
    if _starts_with_directive_marker(line):
        return "directive"
    if _starts_with_footnote_marker(line):
        return "footnote"
    if _starts_with_citation_marker(line):
        return "citation"
    if _starts_with_target(line):
        return "target"
    if _starts_with_substitution_definition(line):
        return "substitution_definition"
    return "comment"


def po2rst(text):
    """Extract msgstr entries from a po content, keeping linenos."""
    output = []
    po = pofile(text, encoding="UTF-8")
    for entry in po.translated_entries():
        # Don't check original msgid, assume it's checked directly.
        while len(output) + 1 < entry.linenum:
            output.append("\n")
        for line in entry.msgstr.splitlines():
            output.append(line + "\n")
    return "".join(output)
