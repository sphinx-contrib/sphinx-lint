from sphinxlint import hide_non_rst_blocks


LITERAL = r"""
Hide non-RST Blocks
===================

This function is intended to filter out literal blocks like this one::

  def enumerate(sequence, start=0):
      n = start
      for elem in sequence:
          yield n, elem
          n += 1

But even if already indented it should work, see the next example.

.. function:: hide_non_rst_blocks(stream)

   This is an indented block, which itself contains a literal, see::

      >>> float('+1.23')
      1.23

      >>> float('   -12345')
      -12345.0

   Yet this line should not be dropped.

This one neither.
"""


LITERAL_EXPECTED = r"""
Hide non-RST Blocks
===================

This function is intended to filter out literal blocks like this one::







But even if already indented it should work, see the next example.

.. function:: hide_non_rst_blocks(stream)

   This is an indented block, which itself contains a literal, see::







   Yet this line should not be dropped.

This one neither.
"""


def test_filter_out_literal():
    out = []
    excluded = []
    for line in hide_non_rst_blocks(
        LITERAL.splitlines(True),
        hidden_block_cb=lambda lineno, block: excluded.append((lineno, block)),
    ):
        out.append(line)
    assert "".join(out) == LITERAL_EXPECTED
    assert (
        excluded[0][1]
        == """
  def enumerate(sequence, start=0):
      n = start
      for elem in sequence:
          yield n, elem
          n += 1

"""
    )
    assert (
        excluded[1][1]
        == """
   >>> float('+1.23')
   1.23

   >>> float('   -12345')
   -12345.0

"""
    )


LITERAL_FUNNY_INDENT = r"""
Hide non-RST Blocks
===================

The case the indentation start high, still flies without really
returning, it should still be skipped::

    Like we start at 4...

    Does not mean we'll keep at 4...

 Maybe we get down at 1
 ======================

 Because why not, at long as we don't get back to the indentation of
 the initial line with the `::`.

But now we're really back out of the block.
"""


LITERAL_FUNNY_INDENT_EXPECTED = r"""
Hide non-RST Blocks
===================

The case the indentation start high, still flies without really
returning, it should still be skipped::











But now we're really back out of the block.
"""


def test_filter_out_funny_indent():
    out = []
    excluded = []
    for line in hide_non_rst_blocks(
        LITERAL_FUNNY_INDENT.splitlines(True),
        hidden_block_cb=lambda lineno, block: excluded.append((lineno, block)),
    ):
        out.append(line)
    assert "".join(out) == LITERAL_FUNNY_INDENT_EXPECTED
    assert (
        excluded[0][1]
        == """
    Like we start at 4...

    Does not mean we'll keep at 4...

 Maybe we get down at 1
 ======================

 Because why not, at long as we don't get back to the indentation of
 the initial line with the `::`.

"""
    )


CODE_BLOCK = """
The code blocks should also be removed, like:

.. code-block:: shell-session

   $ cat multiple_line_file
   Even if there's empty lines

   in the code block.

But not this one.
"""
CODE_BLOCK_EXPECTED = """
The code blocks should also be removed, like:

.. code-block:: shell-session






But not this one.
"""


def test_filter_out_code_block():
    out = []
    excluded = []
    for line in hide_non_rst_blocks(
        CODE_BLOCK.splitlines(True),
        hidden_block_cb=lambda lineno, block: excluded.append((lineno, block)),
    ):
        out.append(line)
    assert "".join(out) == CODE_BLOCK_EXPECTED
    assert (
        excluded[0][1]
        == """
   $ cat multiple_line_file
   Even if there's empty lines

   in the code block.

"""
    )


PRODUCTIONLIST_BLOCK = """
The grammar for a replacement field is as follows:

   .. productionlist:: format-string
      replacement_field: "{" [`field_name`] ["!" `conversion`] [":" `format_spec`] "}"
      field_name: arg_name ("." `attribute_name` | "[" `element_index` "]")*
      arg_name: [`identifier` | `digit`+]
      attribute_name: `identifier`
      element_index: `digit`+ | `index_string`
      index_string: <any source character except "]"> +
      conversion: "r" | "s" | "a"
      format_spec: <described in the next section>

In less formal terms, the replacement field can start with a *field_name* that specifies
the object whose value is to be formatted and inserted
into the output instead of the replacement field.
"""
PRODUCTIONLIST_BLOCK_EXPECTED = """
The grammar for a replacement field is as follows:

   .. productionlist:: format-string









In less formal terms, the replacement field can start with a *field_name* that specifies
the object whose value is to be formatted and inserted
into the output instead of the replacement field.
"""


def test_filter_out_production_list():
    out = []
    for line in hide_non_rst_blocks(PRODUCTIONLIST_BLOCK.splitlines(True)):
        out.append(line)
    assert "".join(out) == PRODUCTIONLIST_BLOCK_EXPECTED


KEEP_THAT = """
The simpler part of :pep:`328` was implemented in Python 2.4: parentheses could now
be used to enclose the names imported from a module using the ``from ... import
...`` statement, making it easier to import many different names.
"""

KEEP_THAT_EXPECTED = """
The simpler part of :pep:`328` was implemented in Python 2.4: parentheses could now
be used to enclose the names imported from a module using the ``from ... import
...`` statement, making it easier to import many different names.
"""


def test_filter_out_dont_filter_out_unwanted_things():
    out = []
    for line in hide_non_rst_blocks(KEEP_THAT.splitlines(True)):
        out.append(line)
    assert "".join(out) == KEEP_THAT_EXPECTED


CONSECUTIVE_PRODUCTION_LIST = """
.. productionlist:: python-grammar
   del_stmt: "del" `target_list`

.. productionlist:: python-grammar
   del_stmt: "del" `target_list`
"""

CONSECUTIVE_PRODUCTION_LIST_EXPECTED = """
.. productionlist:: python-grammar


.. productionlist:: python-grammar

"""


def test_consecutive_production_list():
    out = []
    for line in hide_non_rst_blocks(CONSECUTIVE_PRODUCTION_LIST.splitlines(True)):
        out.append(line)
    assert "".join(out) == CONSECUTIVE_PRODUCTION_LIST_EXPECTED
