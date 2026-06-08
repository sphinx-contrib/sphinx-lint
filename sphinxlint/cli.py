import argparse
import enum
import multiprocessing
import os
import sys
from collections.abc import Iterable, Iterator, Reversible, Sequence
from itertools import chain, starmap
from pathlib import Path
from typing import Any

from sphinxlint import __version__, check_file
from sphinxlint.checkers import Checker, CheckersOptions, all_checkers
from sphinxlint.sphinxlint import LintError

Job = tuple[Path, set[Checker], CheckersOptions | None]


class SortField(enum.Enum):
    """Fields available for sorting error reports"""

    FILENAME = 0
    LINE = 1
    ERROR_TYPE = 2

    @staticmethod
    def as_supported_options() -> str:
        return ",".join(field.name.lower() for field in SortField)


def parse_args(
    argv: list[str] | None = None,
) -> tuple[set[Checker], argparse.Namespace]:
    """Parse command line argument."""
    if argv is None:
        argv = sys.argv
    parser = argparse.ArgumentParser(description=__doc__)

    enabled_checkers_names = {
        checker.name for checker in all_checkers.values() if checker.enabled
    }

    class EnableAction(argparse.Action):
        def __call__(
            self,
            parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            values: str | Sequence[Any] | None,
            option_string: str | None = None,
        ) -> None:
            assert isinstance(values, str)
            if values == "all":
                enabled_checkers_names.update(set(all_checkers.keys()))
            else:
                enabled_checkers_names.update(values.split(","))

    class DisableAction(argparse.Action):
        def __call__(
            self,
            parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            values: str | Sequence[Any] | None,
            option_string: str | None = None,
        ) -> None:
            assert isinstance(values, str)
            if values == "all":
                enabled_checkers_names.clear()
            else:
                enabled_checkers_names.difference_update(values.split(","))

    class StoreSortFieldAction(argparse.Action):
        def __call__(
            self,
            parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            values: str | Sequence[Any] | None,
            option_string: str | None = None,
        ) -> None:
            assert isinstance(values, str)
            sort_fields = []
            for field_name in values.split(","):
                try:
                    sort_fields.append(SortField[field_name.upper()])
                except KeyError:
                    raise ValueError(
                        f"Unsupported sort field: {field_name}, "
                        f"supported values are {SortField.as_supported_options()}"
                    ) from None
            setattr(namespace, self.dest, sort_fields)

    class StoreNumJobsAction(argparse.Action):
        def __call__(
            self,
            parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            values: str | Sequence[Any] | None,
            option_string: str | None = None,
        ) -> None:
            assert isinstance(values, str)
            setattr(namespace, self.dest, self.job_count(values))

        @staticmethod
        def job_count(values: str) -> int:
            if values == "auto":
                return os.cpu_count() or 1
            return max(int(values), 1)

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
        type=str,
        default=[],
    )
    parser.add_argument(
        "-d",
        "--disable",
        action=DisableAction,
        help="comma-separated list of checks to disable. "
        'Give "all" to disable them all. '
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
    parser.add_argument(
        "--max-line-length",
        help="Maximum number of characters on a single line.",
        default=80,
        type=int,
    )
    parser.add_argument(
        "-s",
        "--sort-by",
        action=StoreSortFieldAction,
        help="comma-separated list of fields used to sort errors by. Available "
        f"fields are: {SortField.as_supported_options()}",
    )
    parser.add_argument(
        "-j",
        "--jobs",
        metavar="N",
        action=StoreNumJobsAction,
        help="Run in parallel with N processes. Defaults to 'auto', "
        "which sets N to the number of logical CPUs. "
        "Values <= 1 are all considered 1.",
        default=StoreNumJobsAction.job_count("auto"),
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument("paths", default=[Path(".")], nargs="*", type=Path)
    args = parser.parse_args(argv[1:])
    try:
        enabled_checkers = {all_checkers[name] for name in enabled_checkers_names}
    except KeyError as err:
        print(f"Unknown checker: {err.args[0]}.", file=sys.stderr)
        sys.exit(2)
    return enabled_checkers, args


def walk(path: Path, ignore_list: list[str]) -> Iterator[Path]:
    """Wrapper around os.walk with an ignore list.

    It also allows giving a file, thus yielding just that file.
    """
    if path.is_file():
        if str(path) in ignore_list:
            return
        yield path
        return
    for root, dirs, files in path.walk():
        # ignore subdirs in ignore list
        if any(ignore in str(root) for ignore in ignore_list):
            del dirs[:]
            continue
        for file in files:
            # ignore files in ignore list
            if any(ignore in file for ignore in ignore_list):
                continue
            yield root / file


def _check_file(todo: Job) -> list[LintError]:
    """Wrapper to call check_file with arguments given by
    multiprocessing.imap_unordered."""
    return check_file(*todo)


def sort_errors(
    results: Iterable[list[LintError]], sorted_by: Reversible[SortField]
) -> Iterator[LintError]:
    """Flattens and potentially sorts errors based on user prefernces"""
    if not sorted_by:
        for errors in results:
            yield from errors
        return
    errors = list(error for errors in results for error in errors)
    # sorting is stable in Python, so we can sort in reverse order to get the
    # ordering specified by the user
    for sort_field in reversed(sorted_by):
        if sort_field == SortField.ERROR_TYPE:
            errors.sort(key=lambda error: error.checker_name)
        elif sort_field == SortField.FILENAME:
            errors.sort(key=lambda error: error.filename)
        elif sort_field == SortField.LINE:
            errors.sort(key=lambda error: error.line_no)
    yield from errors


def print_errors(errors: Iterable[LintError]) -> int:
    """Print errors (or a message if nothing is to be printed)."""
    qty = 0
    for error in errors:
        print(error, file=sys.stderr)
        qty += 1
    if qty == 0:
        print("No problems found.")
    return qty


def main(argv: list[str] | None = None) -> int:
    enabled_checkers, args = parse_args(argv)
    options = CheckersOptions.from_argparse(args)
    if args.list:
        if not enabled_checkers:
            print("No checkers selected.")
            return 0
        print(f"{len(enabled_checkers)} checkers selected:")
        for check in sorted(enabled_checkers, key=lambda fct: fct.name):
            if args.verbose:
                print(f"- {check.name}: {check.doc}")
            else:
                print(f"- {check.name}: {check.doc.splitlines()[0]}")
        if not args.verbose:
            print("\n(Use `--list --verbose` to know more about each check)")
        return 0

    for path in args.paths:
        if not os.path.exists(path):
            print(f"Error: path {path} does not exist", file=sys.stderr)
            return 2

    todo = [
        (path, enabled_checkers, options)
        for path in chain.from_iterable(walk(path, args.ignore) for path in args.paths)
    ]

    if args.jobs == 1 or len(todo) < 8:
        count = print_errors(sort_errors(starmap(check_file, todo), args.sort_by))
    else:
        with multiprocessing.Pool(processes=args.jobs) as pool:
            count = print_errors(
                sort_errors(pool.imap_unordered(_check_file, todo), args.sort_by)
            )
            pool.close()
            pool.join()

    return int(bool(count))
