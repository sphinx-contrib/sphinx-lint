A paragraph indented under another paragraph will create a blockquote
and that's usually ok:

   This is an intentional blockquote


In some cases you also have indented directives like ".. index:" that
don't produce any output, so we ignore those too:

   .. index:: ignore

This is also because they might appear in a list like:

(1)
   .. index:: first item

   This is the first item of the list

(2)
   .. index:: second item

   This is the second item of the list


Properly indented nested lists and directives are also ok:

* A list item that contains multiple lines or paragraphs
  should work fine as long as the indentation level is correct

  In this case everything is ok.

* The nested list should be indented under the T:

  * like this
  * and this

*    The start of the list is where the T is:

     * so this should be indented further
     * and this too


* We can also have a directive nested inside a list:

  .. note:: like this


.. note::

   Having text properly indented under a directive is ok

.. note::

   .. note:: Nesting directives is fine too if they are properly indented
