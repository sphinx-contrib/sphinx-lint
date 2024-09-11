.. expect: 15: Excessive indentation in nested section (excessive-indentation)
.. expect: 20: Excessive indentation in nested section (excessive-indentation)
.. expect: 26: Excessive indentation in nested section (excessive-indentation)
.. expect: 30: Excessive indentation in nested section (excessive-indentation)
.. expect: 35: Excessive indentation in nested section (excessive-indentation)
.. expect: 42: Excessive indentation in nested section (excessive-indentation)
.. expect: 49: Excessive indentation in nested section (excessive-indentation)
.. expect: 51: Excessive indentation in nested section (excessive-indentation)
.. expect: 53: Excessive indentation in nested section (excessive-indentation)
.. expect: 57: Excessive indentation in nested section (excessive-indentation)


The most common mistakes is indenting lists and directives under a paragraph:

  * This list shouldn't be indented
  * Otherwise it's rendered inside a blockquote

Directives also shouldn't be indented under a paragraph:

  .. note:: like this one



* Nested lists should be indented properly

    * the bullet of this list should have been under the N

* Same goes for directives

    .. note:: this should have been under the S


.. note::

     * the opposite is also true
     * lists nested under directives
     * should be indented properly
     * (but maybe they don't have to?)

.. note::

     .. note:: this is also not allowed atm, but maybe it should


There are also other types of lists:

* bullet lists

    - bullet lists with different bullets

        1. numbered lists

             2) more numbered lists

                (3) numbered lists with more parentheses

                      #. autonumbered lists


Each of these should give an error, since they are all indented wrong.

Numbered lists that start with letters (a. b. c. ...)
and roman numerals (I. II. III. ...) are only supported by Sphinx 7+
so we just ignore them
