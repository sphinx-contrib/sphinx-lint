from dataclasses import dataclass
from os.path import splitext
from pathlib import Path

from sphinxlint.checkers import Checker, CheckersOptions
from sphinxlint.utils import PER_FILE_CACHES, hide_non_rst_blocks, po2rst


@dataclass(frozen=True)
class LintError:
    """A linting error found by one of the checkers"""

    filename: str
    line_no: int
    msg: str
    checker_name: str

    def __str__(self) -> str:
        assert self.checker_name
        return f"{self.filename}:{self.line_no}: {self.msg} ({self.checker_name})"


def check_text(
    filename: str,
    text: str,
    checkers: set[Checker],
    options: CheckersOptions | None = None,
) -> list[LintError]:
    if options is None:
        options = CheckersOptions()
    errors = []
    lines_with_rst_only: tuple[str, ...] = ()
    ext = splitext(filename)[1]
    checkers = {checker for checker in checkers if ext in checker.suffixes}
    lines = tuple(text.splitlines(keepends=True))
    if any(checker.rst_only for checker in checkers):
        lines_with_rst_only = hide_non_rst_blocks(lines)
    for check in checkers:
        if ext not in check.suffixes:
            continue
        for lno, msg in check(
            filename, lines_with_rst_only if check.rst_only else lines, options
        ):
            errors.append(LintError(filename, lno, msg, check.name))
    return errors


def check_file(
    filepath: Path, checkers: set[Checker], options: CheckersOptions | None = None
) -> list[LintError]:
    if options is None:
        options = CheckersOptions()
    try:
        ext = splitext(filepath)[1]
        if not any(ext in checker.suffixes for checker in checkers):
            return []
        try:
            with open(filepath, encoding="utf-8") as f:
                text = f.read()
            if filepath.suffix == ".po":
                text = po2rst(text)
        except OSError as err:
            return [
                LintError(
                    str(filepath), 0, f"{filepath}: cannot open: {err}", "check_file"
                )
            ]
        except UnicodeDecodeError as err:
            return [
                LintError(
                    str(filepath), 0, f"cannot decode as UTF-8: {err}", "check_file"
                )
            ]
        return check_text(str(filepath), text, checkers, options)
    finally:
        for memoized_function in PER_FILE_CACHES:
            memoized_function.cache_clear()
