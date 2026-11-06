"""Benchmarks run via pytest-codspeed."""

import pytest

from sphinxlint import check_text
from sphinxlint.checkers import all_checkers
from sphinxlint.cli import main
from sphinxlint.sphinxlint import CheckersOptions
from sphinxlint.utils import (
    PER_FILE_CACHES,
    clean_paragraph,
    escape2null,
    hide_non_rst_blocks,
    paragraphs,
)

FILENAME = "benchmark.rst"

# A bit of everything found in a typical documentation page.
SECTION = r"""
Section NNN
===========

.. _target-NNN:

The :mod:`!spamNNN` module provides :class:`~spam.Eggs` objects and the
:func:`spam.fry` function.  See :pep:`8` and :ref:`target-NNN` for details,
or the `project homepage <https://example.com/spam/NNN>`_.

Plain prose paragraph number NNN without any markup at all, as is the case
for most of the paragraphs in most documentation.  It talks about spam, eggs,
bacon and sausages; it has a sentence (with parentheses) and some "quotes".

Use ``spam.fry(NNN)`` to fry, or ``spam.boil()`` to boil; ``None`` is
returned when ``eggs`` is empty.  An escaped asterisk \* and backslash \\
show up next to *emphasis* and **strong emphasis** number NNN.

.. function:: fry(eggs, *, bacon=NNN)

   Fry *eggs* NNN times.  Return a :class:`list` of ``Fried`` instances.

   .. versionchanged:: 3.NNN
      Added the *bacon* parameter.

   .. note::

      This is a note mentioning :exc:`ValueError`, the `tracker`__ and the
      :term:`iterable` glossary entry.

__ https://example.com/tracker/NNN

Example NNN::

   >>> import spam
   >>> spam.fry([NNN])  # `not a role` and :func:`not checked`
   ['fried']

.. code-block:: python

   def fry(eggs):
       return [f"fried {egg}" for egg in eggs]

.. A comment about section NNN, which is hidden from the checkers.

+----------+------------------+
| Name     | Meaning          |
+==========+==================+
| ``spam`` | :class:`Spam`    |
+----------+------------------+
| ``eggs`` | Eggs number NNN  |
+----------+------------------+

* A list item with a :meth:`~Spam.fry` method reference.
* Another item, with an `external link <https://example.org/NNN>`__.

#. First step NNN.
#. Second step, see :ref:`the target <target-NNN>`.
"""

# Number each section so its paragraphs differ from the other sections':
# identical ones would be served from the per-file caches.
TEXT = "".join(SECTION.replace("NNN", str(n)) for n in range(25))
LINES = tuple(TEXT.splitlines(keepends=True))
RST_LINES = hide_non_rst_blocks(LINES)
PARAGRAPHS = [paragraph for _, paragraph in paragraphs(RST_LINES)]

OPTIONS = CheckersOptions()
RST_CHECKERS = [
    checker for _, checker in sorted(all_checkers.items()) if ".rst" in checker.suffixes
]
ENABLED_CHECKERS = [checker for checker in RST_CHECKERS if checker.enabled]


def clear_caches():
    # Like check_file does after each file,
    # so each benchmark round does the work again.
    for memoized_function in PER_FILE_CACHES:
        memoized_function.cache_clear()


@pytest.fixture(autouse=True)
def _clear_caches():
    clear_caches()


def run_check_text(checkers):
    errors = check_text(FILENAME, TEXT, checkers, OPTIONS)
    clear_caches()
    return errors


def run_checker(checker):
    lines = RST_LINES if checker.rst_only else LINES
    return list(checker(FILENAME, lines, OPTIONS))


def test_check_text_enabled_checkers(benchmark):
    benchmark(run_check_text, ENABLED_CHECKERS)


def test_check_text_all_checkers(benchmark):
    benchmark(run_check_text, RST_CHECKERS)


@pytest.mark.parametrize("checker", RST_CHECKERS, ids=lambda checker: checker.name)
def test_checker(benchmark, checker):
    # Warm the per-file caches to benchmark the checker's own work,
    # not the helpers it shares with others: those have their own benchmarks.
    run_checker(checker)
    benchmark(run_checker, checker)


def test_hide_non_rst_blocks(benchmark):
    def hide():
        hide_non_rst_blocks(LINES)
        clear_caches()

    benchmark(hide)


def test_paragraphs(benchmark):
    def split():
        paragraphs(RST_LINES)
        clear_caches()

    benchmark(split)


def test_escape2null(benchmark):
    def escape():
        for paragraph in PARAGRAPHS:
            escape2null(paragraph)
        clear_caches()

    benchmark(escape)


def test_clean_paragraph(benchmark):
    def clean():
        for paragraph in PARAGRAPHS:
            clean_paragraph(paragraph)
        clear_caches()

    benchmark(clean)


def test_clean_paragraph_lines(benchmark):
    # check_default_role cleans line by line.
    def clean():
        for line in RST_LINES:
            clean_paragraph(line)
        clear_caches()

    benchmark(clean)


def test_main(benchmark, tmp_path):
    file = tmp_path / FILENAME
    file.write_text(TEXT, encoding="UTF-8")
    benchmark(main, ["sphinxlint.py", "--jobs", "1", str(file)])
