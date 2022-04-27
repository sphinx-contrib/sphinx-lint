import argparse
import multiprocessing
import os
import sys
from collections import Counter
from functools import reduce
from itertools import chain, starmap

from sphinxlint import check_file
from sphinxlint import rst
from sphinxlint.config import get_config
from sphinxlint.checkers import all_checkers
from sphinxlint.sphinxlint import CheckersOptions


def parse_args(argv=None):
    """Parse command line argument."""
    if argv is None:
        argv = sys.argv
    if argv[1:2] == ["init", "directives"]:
        from directivegetter import collect_directives

        raise SystemExit(collect_directives(argv[2:]))

    parser = argparse.ArgumentParser(description=__doc__)

    enabled_checkers_names = {
        checker.name for checker in all_checkers.values() if checker.enabled
    }

    class EnableAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            if values == "all":
                enabled_checkers_names.update(set(all_checkers.keys()))
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
    parser.add_argument(
        "--max-line-length",
        help="Maximum number of characters on a single line.",
        default=80,
        type=int,
    )
    parser.add_argument("paths", default=".", nargs="*")
    args = parser.parse_args(argv[1:])
    try:
        enabled_checkers = {all_checkers[name] for name in enabled_checkers_names}
    except KeyError as err:
        print(f"Unknown checker: {err.args[0]}.")
        sys.exit(2)
    return enabled_checkers, args


def walk(path, ignore_list):
    """Wrapper around os.walk with an ignore list.

    It also allows giving a file, thus yielding just that file.
    """
    if os.path.isfile(path):
        if path in ignore_list:
            return
        yield path if path[:2] != "./" else path[2:]
        return
    for root, dirs, files in os.walk(path):
        # ignore subdirs in ignore list
        if any(ignore in root for ignore in ignore_list):
            del dirs[:]
            continue
        for file in files:
            file = os.path.join(root, file)
            # ignore files in ignore list
            if any(ignore in file for ignore in ignore_list):
                continue
            yield file if file[:2] != "./" else file[2:]


def main(argv=None):
    config = get_config()

    # Append extra directives
    rst.DIRECTIVES_CONTAINING_ARBITRARY_CONTENT.extend(config.get("known_directives", []))

    enabled_checkers, args = parse_args(argv)
    options = CheckersOptions.from_argparse(args)
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
        if not os.path.exists(path):
            print(f"Error: path {path} does not exist")
            return 2

    todo = [
        (path, enabled_checkers, options)
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
