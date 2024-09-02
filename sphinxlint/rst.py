"""Constants, regexes, and function generating regexes to "parse" reStructuredText.

In this file:
- All constants are ALL_CAPS
- All compiled regexes are suffixed by _RE
"""

from functools import lru_cache

import regex as re

DELIMITERS = (
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

CLOSERS = (
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

OPENERS = (
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
DIRECTIVES_CONTAINING_RST = [
    # standard docutils ones
    'admonition', 'attention', 'caution', 'class', 'compound', 'container',
    'danger', 'epigraph', 'error', 'figure', 'footer', 'header', 'highlights',
    'hint', 'image', 'important', 'include', 'line-block', 'list-table', 'meta',
    'note', 'parsed-literal', 'pull-quote', 'replace', 'sidebar', 'tip', 'topic',
    'warning',
    # Sphinx and Python docs custom ones
    'acks', 'attribute', 'autoattribute', 'autoclass', 'autodata',
    'autoexception', 'autofunction', 'automethod', 'automodule',
    'availability', 'centered', 'cfunction', 'class', 'classmethod', 'cmacro',
    'cmdoption', 'cmember', 'confval', 'cssclass', 'ctype',
    'currentmodule', 'cvar', 'data', 'decorator', 'decoratormethod',
    'deprecated-removed', 'deprecated(?!-removed)', 'describe', 'directive',
    'envvar', 'event', 'exception', 'function', 'glossary',
    'highlight', 'highlightlang', 'impl-detail', 'index', 'literalinclude',
    'method', 'miscnews', 'module', 'moduleauthor', 'opcode', 'pdbcommand',
    'program', 'role', 'sectionauthor', 'seealso',
    'sourcecode', 'staticmethod', 'tabularcolumns', 'testcode', 'testoutput',
    'testsetup', 'toctree', 'todo', 'todolist', 'versionadded',
    'versionchanged', 'c:function', 'coroutinefunction'
]

DIRECTIVES_CONTAINING_ARBITRARY_CONTENT = [
    # standard docutils ones
    'contents', 'csv-table', 'date',  'default-role', 'include', 'raw',
    'restructuredtext-test-directive', 'role', 'rubric', 'sectnum', 'table',
    'target-notes', 'title', 'unicode',
    # Sphinx and Python docs custom ones
    'code-block', 'doctest', 'productionlist',
]

# fmt: on

DIRECTIVES_CONTAINING_ARBITRARY_CONTENT_RE = re.compile(
    r"^\s*\.\. (" + "|".join(DIRECTIVES_CONTAINING_ARBITRARY_CONTENT) + ")::"
)

DIRECTIVES_CONTAINING_RST_RE = re.compile(
    r"^\s*\.\. (" + "|".join(DIRECTIVES_CONTAINING_RST) + ")::"
)

ALL_DIRECTIVES = (
    "("
    + "|".join(DIRECTIVES_CONTAINING_RST + DIRECTIVES_CONTAINING_ARBITRARY_CONTENT)
    + ")"
)

QUOTE_PAIRS = [
    "»»",  # Swedish
    "‘‚",  # Albanian/Greek/Turkish
    "’’",  # Swedish
    "‚‘",  # German
    "‚’",  # Polish
    "“„",  # Albanian/Greek/Turkish
    "„“",  # German
    "„”",  # Polish
    "””",  # Swedish
    "››",  # Swedish
    "''",  # ASCII
    '""',  # ASCII
    "<>",  # ASCII
    "()",  # ASCII
    "[]",  # ASCII
    "{}",  # ASCII
]


QUOTE_PAIRS_NEGATIVE_LOOKBEHIND = (
    "(?<!"
    + "|".join(f"{re.escape(pair[0])}`{re.escape(pair[1])}" for pair in QUOTE_PAIRS)
    + "|"
    + "|".join(
        f"{opener}`{closer}"
        for opener, closer in zip(map(re.escape, OPENERS), map(re.escape, CLOSERS))
    )
    + ")"
)

SIMPLENAME = r"(?:(?!_)\w)+(?:[-._+:](?:(?!_)\w)+)*"

# The following chars groups are from docutils:
CLOSING_DELIMITERS = "\\\\.,;!?"

BEFORE_ROLE = r"(^|(?<=[\s(/'{\[*-]))"
ROLE_TAG = rf":{SIMPLENAME}:"
ROLE_HEAD = rf"({BEFORE_ROLE}:{SIMPLENAME}:)"  # A role, with a clean start

ASCII_ALLOWED_BEFORE_INLINE_MARKUP = r"""-:/'"<(\[{"""
UNICODE_ALLOWED_BEFORE_INLINE_MARKUP = r"\p{Ps}\p{Pi}\p{Pf}\p{Pd}\p{Po}"
ASCII_ALLOWED_AFTER_INLINE_MARKUP = r"""-.,:;!?/'")\]}>"""
UNICODE_ALLOWED_AFTER_INLINE_MARKUP = r"\p{Pe}\p{Pi}\p{Pf}\p{Pd}\p{Po}"


@lru_cache(maxsize=None)
def inline_markup_gen(start_string, end_string, extra_allowed_before=""):
    """Generate a regex matching an inline markup.

    inline_markup_gen('**', '**') geneates a regex matching strong
    emphasis inline markup.
    """
    if extra_allowed_before:
        extra_allowed_before = "|" + extra_allowed_before
    return re.compile(
        rf"""
    (?<!\x00) # Both inline markup start-string and end-string must not be preceded by
              # an unescaped backslash

    (?<=             # Inline markup start-strings must:
        ^|           # start a text block
        \s|          # or be immediately preceded by whitespace,
        [{ASCII_ALLOWED_BEFORE_INLINE_MARKUP}]|  # one of the ASCII characters
        [{UNICODE_ALLOWED_BEFORE_INLINE_MARKUP}] # or a similar non-ASCII
                                                 # punctuation character.
        {extra_allowed_before}
    )

    (?P<inline_markup>
        {start_string} # Inline markup start
        \S             # Inline markup start-strings must be immediately followed by
                       # non-whitespace.
                       # The inline markup end-string must be separated by at least one
                       # character from the start-string.
        {QUOTE_PAIRS_NEGATIVE_LOOKBEHIND}
        .*?
        (?<=\x00\ |\S)# Inline markup end-strings must be immediately preceded
                      # by non-whitespace.
        {end_string}  # Inline markup end
    )

    (?=       # Inline markup end-strings must
        $|    # end a text block or
        \s|   # be immediately followed by whitespace,
        \x00|
        [{ASCII_ALLOWED_AFTER_INLINE_MARKUP}]|  # one of the ASCII characters
        [{UNICODE_ALLOWED_AFTER_INLINE_MARKUP}] # or a similar non-ASCII
                                                # punctuation character.
    )
    """,
        flags=re.VERBOSE | re.DOTALL,
    )


# https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#inline-markup-recognition-rules
INTERPRETED_TEXT_RE = inline_markup_gen("`", "`")
INLINE_INTERNAL_TARGET_RE = inline_markup_gen("_`", "`")
HYPERLINK_REFERENCES_RE = inline_markup_gen("`", "`_")
ANONYMOUS_HYPERLINK_REFERENCES_RE = inline_markup_gen("`", "`__")
INLINE_LITERAL_RE = inline_markup_gen("``", "``")
NORMAL_ROLE_RE = re.compile(
    rf"""
    (?<!\x00) # Both inline markup start-string and end-string must not be preceded by
              # an unescaped backslash

    (?<=             # Inline markup start-strings must:
        ^|           # start a text block
        \s|          # or be immediately preceded by whitespace,
        [{ASCII_ALLOWED_BEFORE_INLINE_MARKUP}]|  # one of the ASCII characters
        [{UNICODE_ALLOWED_BEFORE_INLINE_MARKUP}] # or a similar non-ASCII
                                                 # punctuation character.
    )

    :{SIMPLENAME}:{INTERPRETED_TEXT_RE.pattern}""",
    flags=re.VERBOSE | re.DOTALL,
)

BACKTICK_IN_FRONT_OF_ROLE_RE = re.compile(
    rf"(^|\s)`:{SIMPLENAME}:{INTERPRETED_TEXT_RE.pattern}", flags=re.VERBOSE | re.DOTALL
)

# Find comments that look like a directive, like:
# .. versionchanged 3.6
# or
# .. versionchanged: 3.6
# as it should be:
# .. versionchanged:: 3.6
SEEMS_DIRECTIVE_RE = re.compile(rf"^\s*(?<!\.)\.\. {ALL_DIRECTIVES}([^a-z:]|:(?!:))")

# Find directive prefixed with three dots instead of two, like:
# ... versionchanged:: 3.6
# instead of:
# .. versionchanged:: 3.6
THREE_DOT_DIRECTIVE_RE = re.compile(rf"\.\.\. {ALL_DIRECTIVES}::")

# Find role used with double backticks instead of simple backticks like:
# :const:``None``
# instead of:
# :const:`None`
DOUBLE_BACKTICK_ROLE_RE = re.compile(rf"(?<!``){ROLE_HEAD}``")

START_STRING_PREFIX = f"(^|(?<=\\s|[{OPENERS}{DELIMITERS}|]))"
END_STRING_SUFFIX = f"($|(?=\\s|[\x00{CLOSING_DELIMITERS}{DELIMITERS}{CLOSERS}|]))"

# Find role glued with another word like:
#     the:c:func:`PyThreadState_LeaveTracing` function.
# instead of:
#     the :c:func:`PyThreadState_LeaveTracing` function.
#
# Also finds roles missing their leading colon like:
#     issue:`123`
# instead of:
#     :issue:`123`

ROLE_GLUED_WITH_WORD_RE = re.compile(rf"(^|\s)(?<!:){SIMPLENAME}:`(?!`)")

ROLE_WITH_NO_BACKTICKS_RE = re.compile(rf"(^|\s):{SIMPLENAME}:(?![`:])[^\s`]+(\s|$)")

# Find role missing middle colon, like:
#    The :issue`123` is ...
ROLE_MISSING_RIGHT_COLON_RE = re.compile(rf"(^|\s):{SIMPLENAME}`(?!`)")


SEEMS_HYPERLINK_RE = re.compile(r"`[^`]+?(\s?)<https?://[^`]+>`(_?)")

LEAKED_MARKUP_RE = re.compile(r"[a-z]::\s|`|\.\.\s*\w+:")

TRIPLE_BACKTICKS_RE = re.compile(
    rf"(?:{START_STRING_PREFIX})```[^`]+?(?<!{START_STRING_PREFIX})```(?:{END_STRING_SUFFIX})"
)

ROLE_MISSING_CLOSING_BACKTICK_RE = re.compile(rf"({ROLE_HEAD}`[^`]+?)[^`]*$")

ROLE_WITH_UNNECESSARY_PARENTHESES_RE = re.compile(r"(^|\s):(func|meth):`[^`]+\(\)`")
