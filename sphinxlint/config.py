import sys
from os.path import isfile
from typing import Any

if sys.version_info[:2] >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


def _read_toml(filename: str) -> dict[str, Any]:
    if tomllib is None:
        return {}
    with open(filename, "rb") as f:
        return tomllib.load(f)


def get_config() -> dict[str, Any]:
    if isfile("sphinx.toml"):
        table = _read_toml("sphinx.toml")
    elif isfile("pyproject.toml"):
        table = _read_toml("pyproject.toml")
    else:
        table = {}
    return table.get("tool", {}).get("sphinx-lint", {})
