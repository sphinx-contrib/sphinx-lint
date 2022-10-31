from collections import Counter
from os.path import splitext

from sphinxlint.utils import hide_non_rst_blocks, po2rst


class CheckersOptions:
    """Configuration options for checkers."""

    max_line_length = 80

    @classmethod
    def from_argparse(cls, namespace):
        options = cls()
        options.max_line_length = namespace.max_line_length
        return options


def check_text(filename, text, checkers, options=None):
    if options is None:
        options = CheckersOptions()
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
            filename, lines_with_rst_only if check.rst_only else lines, options
        ):
            print(f"{filename}:{lno}: {msg} ({check.name})")
            errors[check.name] += 1
    return errors


def check_file(filename, checkers, options: CheckersOptions = None):
    ext = splitext(filename)[1]
    if not any(ext in checker.suffixes for checker in checkers):
        return Counter()
    try:
        with open(filename, encoding="utf-8") as f:
            text = f.read()
        if filename.endswith(".po"):
            text = po2rst(text)
    except OSError as err:
        print(f"{filename}: cannot open: {err}")
        return Counter({4: 1})
    except UnicodeDecodeError as err:
        print(f"{filename}: cannot decode as UTF-8: {err}")
        return Counter({4: 1})
    return check_text(filename, text, checkers, options)
