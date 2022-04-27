from __future__ import annotations

from pathlib import Path
import sys
from typing import TYPE_CHECKING

from docutils.parsers.rst.directives import _directive_registry, _directives
from docutils.parsers.rst.languages import en
from sphinx.builders.dummy import DummyBuilder

if TYPE_CHECKING:
    from collections.abc import Iterator, Iterable

    from sphinx.application import Sphinx

DOCUTILS_DIRECTIVES = frozenset(_directive_registry.keys() | en.directives.keys())
SPHINX_DIRECTIVES = frozenset({
    # reStructuredText content:
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # Added by Sphinx:
    'acks', 'centered', 'codeauthor', 'default-domain', 'deprecated(?!-removed)',
    'describe', 'highlight', 'hlist', 'index', 'literalinclude', 'moduleauthor',
    'object', 'only', 'rst-class', 'sectionauthor', 'seealso', 'tabularcolumns',
    'toctree', 'versionadded', 'versionchanged',
    # Added by Sphinx (since removed):
    'highlightlang',  # removed in Sphinx 4.0
    # Added by Sphinx (Standard domain):
    'cmdoption', 'envvar', 'glossary', 'option', 'productionlist', 'program',
    # Added by Sphinx (Python domain):
    'py:attribute', 'py:class', 'py:classmethod', 'py:currentmodule', 'py:data',
    'py:decorator', 'py:decoratormethod', 'py:exception', 'py:function',
    'py:method', 'py:module', 'py:property', 'py:staticmethod',
    'attribute', 'class', 'classmethod', 'currentmodule', 'data',
    'decorator', 'decoratormethod', 'exception', 'function',
    'method', 'module', 'property', 'staticmethod',
    # Added by Sphinx (C domain):
    'c:alias', 'c:enum', 'c:enumerator', 'c:function', 'c:macro', 'c:member',
    'c:struct', 'c:type', 'c:union', 'c:var',
    'cfunction', 'cmacro', 'cmember', 'ctype', 'cvar',
    # Added by Sphinx (sphinx.ext.todo):
    'todo', 'todolist',
    # Added in Sphinx's own documentation only:
    'confval', 'event',

    # Arbitrary content:
    # ~~~~~~~~~~~~~~~~~~
    # Added by Sphinx (core):
    'cssclass',
    # Added by Sphinx (Standard domain):
    'productionlist',
    # Added by Sphinx (C domain):
    'c:namespace', 'c:namespace-pop', 'c:namespace-push',
    # Added by Sphinx (sphinx.ext.autodoc):
    'autoattribute', 'autoclass', 'autodata', 'autodecorator', 'autoexception',
    'autofunction', 'automethod', 'automodule', 'autonewtypedata',
    'autonewvarattribute', 'autoproperty',
    # Added by Sphinx (sphinx.ext.doctest):
    'doctest', 'testcleanup', 'testcode', 'testoutput', 'testsetup',

})
CORE_DIRECTIVES = DOCUTILS_DIRECTIVES | SPHINX_DIRECTIVES


def tomlify_directives(directives: Iterable[str], comment: str) -> Iterator[str]:
    yield f"    # {comment}:"
    yield from (f'    "{directive}",' for directive in sorted(directives))


def write_directives(directives: Iterable[str]):
    lines = [
        "[tool.sphinx-lint]",
        "known_directives = [",
        tomlify_directives(directives, "Added by extensions or in conf.py"),
        "]",
        "",  # final blank line
    ]
    with open("sphinx.toml", "w", encoding="utf-8") as file:
        file.write("\n".join(lines))


class DirectiveCollectorBuilder(DummyBuilder):
    name = "directive_collector"

    def get_outdated_docs(self) -> str:
        return "nothing, just getting list of directives"

    def read(self) -> list[str]:
        write_directives({*_directives} - CORE_DIRECTIVES)
        return []

    def write(self, *args, **kwargs) -> None:
        pass


def setup(app: Sphinx) -> dict[str, bool]:
    """Plugin for Sphinx"""
    app.add_builder(DirectiveCollectorBuilder)
    return {"parallel_read_safe": True, "parallel_write_safe": True}


def collect_directives():
    from sphinx import application
    from sphinx.application import Sphinx

    try:
        source_dir, build_dir, *opts = sys.argv[1:]
    except ValueError:
        raise RuntimeError("Two arguments (source dir and build dir) are required.")

    application.builtin_extensions = (
        *application.builtin_extensions,
        "directivegetter"  # set up this file as an extension
    )
    app = Sphinx(
        str(Path(source_dir)),
        str(Path(source_dir)),
        str(Path(build_dir)),
        str(Path(build_dir, "doctrees")),
        "directive_collector",
    )
    app.build(force_all=True)
    raise SystemExit(app.statuscode)


if __name__ == "__main__":
    collect_directives()
